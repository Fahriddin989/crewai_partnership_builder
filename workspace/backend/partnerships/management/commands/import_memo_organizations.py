"""Import public Memo organization cards and correct their five requested fields."""
from collections import Counter
import json
from pathlib import Path
import re
import unicodedata

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from partnerships.models import Organization
from partnerships.serializers import OrganizationSerializer


def normalize(value):
    value = unicodedata.normalize('NFKC', value).casefold()
    value = value.translate(str.maketrans('', '', "'\"‘’ʼʻ`´«»“”"))
    return re.sub(r'[\W_]+', '', value)


COUNTRIES = {
    'Uzbekistan': ['Uzbekistan', 'Republic of Uzbekistan', 'Uzbekistan Republic', 'Узбекистан', 'Республика Узбекистан', 'Oʻzbekiston', 'UZ', 'UZB'],
    'Russia': ['Russia', 'Russian Federation', 'Россия', 'Российская Федерация', 'RU', 'RUS'],
    'Kazakhstan': ['Kazakhstan', 'Казахстан', 'Республика Казахстан', 'KZ', 'KAZ'],
    'China': ['China', 'PRC', 'Китай', 'КНР', 'CN', 'CHN'],
    'Poland': ['Poland', 'Польша', 'PL', 'POL'],
    'Italy': ['Italy', 'Italia', 'Италия', 'IT', 'ITA'],
    'Bangladesh': ['Bangladesh', 'Бангладеш', 'BD', 'BGD'],
    'Lithuania': ['Lithuania', 'Литва', 'LT', 'LTU'],
    'Turkey': ['Turkey', 'Türkiye', 'Turkiye', 'Турция', 'TR', 'TUR'],
    'Singapore': ['Singapore', 'Сингапур', 'SG', 'SGP'],
    'Israel': ['Israel', 'Израиль', 'IL', 'ISR'],
    'United States': ['United States', 'United States of America', 'USA', 'US', 'США'],
    'Germany': ['Germany', 'Deutschland', 'Германия', 'DE', 'DEU'],
}
COUNTRY_KEYS = {normalize(alias): normalize(country) for country, aliases in COUNTRIES.items() for alias in aliases}


def country_key(value):
    key = normalize(value)
    return COUNTRY_KEYS.get(key, key)


class Command(BaseCommand):
    help = 'Preview or import Memo cards: name, type, country, website and public visibility.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('--data', type=Path, default=Path(__file__).resolve().parents[2] / 'data' / 'memo_organizations.json')
        parser.add_argument('--apply', action='store_true', help='Create missing cards and update the five requested fields; default: read-only preview.')
        parser.add_argument('--username', help='Optional existing user to record in created_by and updated_by.')

    def handle(self, *args, **options):
        try:
            dataset = json.loads(options['data'].read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise CommandError(f'Unable to read input data: {exc}') from exc
        if not isinstance(dataset, dict) or dataset.get('schema_version') != 1 or not isinstance(dataset.get('organizations'), list):
            raise CommandError('Expected schema_version 1 and an organizations array.')

        actor = None
        if options['username']:
            User = get_user_model()
            try:
                actor = User._default_manager.get(**{User.USERNAME_FIELD: options['username']})
            except User.DoesNotExist as exc:
                raise CommandError('The supplied username does not exist.') from exc

        rows, pending, keys, identities = [], [], set(), {}
        fields = ('name', 'organization_type', 'country', 'website', 'description', 'is_public', 'academic_unit_ids')
        for row in dataset['organizations']:
            if not isinstance(row, dict) or not isinstance(row.get('record_key'), str):
                raise CommandError('Each organization needs a record_key.')
            key = row['record_key']
            if key in keys:
                raise CommandError(f'Duplicate record_key: {key}')
            keys.add(key)
            if row.get('ready_for_import') is False:
                pending.append(key)
                continue
            if row.get('ready_for_import') is not True:
                raise CommandError(f'{key}: ready_for_import must explicitly be true or false.')
            if row.get('is_public') is not True or row.get('academic_unit_ids') != []:
                raise CommandError(f'{key}: this import requires public organizations and no new direction assignments.')
            for field in ('name', 'country', 'organization_type', 'website'):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    raise CommandError(f'{key}: {field} must be a nonempty string.')
            aliases = row.get('aliases', [])
            if not isinstance(aliases, list) or any(not isinstance(alias, str) or not alias.strip() for alias in aliases):
                raise CommandError(f'{key}: aliases must be nonempty strings.')
            payload = {field: row.get(field) for field in fields}
            serializer = OrganizationSerializer(data=payload)
            if not serializer.is_valid():
                raise CommandError(f'{key}: {serializer.errors}')
            names = {normalize(row['name'])} | {normalize(alias) for alias in aliases}
            for name in names:
                identity = (country_key(row['country']), name)
                if identity in identities and identities[identity] != key:
                    raise CommandError(f'Input aliases overlap: {identities[identity]} and {key}.')
                identities[identity] = key
            rows.append((row, names))

        actor_label = options['username'] or '(none; existing audit users are preserved)'
        self.stdout.write(f'Mode: {"APPLY" if options["apply"] else "PREVIEW - no changes"}; audit user: {actor_label}')
        created, updated, unchanged, conflicts = [], [], [], []
        update_fields = ('name', 'organization_type', 'country', 'website', 'is_public')
        # Plan before writing, then save the whole batch in one transaction.
        with transaction.atomic():
            by_name = {}
            organizations = Organization.objects.all()
            if options['apply']:
                organizations = organizations.select_for_update()
            for org in organizations:
                by_name.setdefault(normalize(org.name), {})[org.pk] = org
            plans = []
            for row, names in rows:
                matches = {}
                for name in names:
                    matches.update(by_name.get(name, {}))
                same_country = [org for org in matches.values() if country_key(org.country) == country_key(row['country'])]
                # A unique name may have an incorrect/missing country from an earlier import.
                candidate = same_country[0] if len(same_country) == 1 else next(iter(matches.values())) if len(matches) == 1 else None
                if matches and candidate is None:
                    conflicts.append(row['record_key'])
                    self.stdout.write(self.style.WARNING(f'CONFLICT {row["record_key"]}: {row["name"]}; existing IDs {sorted(matches)}. Skipped.'))
                else:
                    plans.append((row, candidate))
            claims = Counter(org.pk for _, org in plans if org is not None)
            for row, org in plans:
                key = row['record_key']
                if org is not None and claims[org.pk] > 1:
                    conflicts.append(key)
                    self.stdout.write(self.style.WARNING(f'CONFLICT {key}: multiple input rows match existing ID {org.pk}. Skipped.'))
                    continue
                if org is None:
                    if options['apply']:
                        serializer = OrganizationSerializer(data={field: row[field] for field in fields})
                        if not serializer.is_valid():
                            raise CommandError(f'{key}: {serializer.errors}')
                        serializer.save(created_by=actor, updated_by=actor)
                    created.append(key)
                    action = 'CREATED' if options['apply'] else 'WOULD CREATE'
                else:
                    changes = {field: row[field] for field in update_fields if getattr(org, field) != row[field]}
                    if not changes:
                        unchanged.append(key)
                        action = 'UNCHANGED'
                    else:
                        if options['apply']:
                            # Omit descriptions and academic_unit_ids so manual work is retained.
                            serializer = OrganizationSerializer(org, data=changes, partial=True)
                            if not serializer.is_valid():
                                raise CommandError(f'{key}: {serializer.errors}')
                            serializer.save(**({'updated_by': actor} if actor is not None else {}))
                        updated.append(key)
                        action = ('UPDATED' if options['apply'] else 'WOULD UPDATE') + ' [' + ', '.join(changes) + ']'
                if options['verbosity'] >= 2:
                    self.stdout.write(f'{action} {key}: {row["name"]}')

        create_verb, update_verb = ('Created', 'updated') if options['apply'] else ('Would create', 'would update')
        self.stdout.write(self.style.SUCCESS(f'{create_verb}: {len(created)}; {update_verb}: {len(updated)}; unchanged: {len(unchanged)}; conflicts skipped: {len(conflicts)}; pending review skipped: {len(pending)}.'))
        if pending:
            self.stdout.write('Pending review: '+', '.join(pending)+'. See ORGANIZATIONS_REVIEW_RU.md.')
        self.stdout.write('Only Organization cards are imported. Agreements, contacts, files, directions and activities are handled separately.')
