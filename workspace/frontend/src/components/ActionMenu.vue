<template>
  <div ref="root" class="action-menu"><button ref="trigger" class="overflow-button" aria-label="Actions" aria-haspopup="menu" :aria-expanded="open" @click.stop="toggle">⋯</button></div>
  <Teleport to="body"><div v-if="open" ref="popover" class="action-popover action-popover-fixed" role="menu" :style="positionStyle" @click.stop><button role="menuitem" @click="choose('edit')">Edit</button><button role="menuitem" :class="deleteClass" @click="choose('delete')">{{ deleteLabel }}</button></div></Teleport>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
defineProps({ deleteLabel: { type: String, default: 'Delete' }, deleteClass: { type: String, default: 'danger-text' } })
const emit = defineEmits(['edit', 'delete'])
const root=ref(null),trigger=ref(null),popover=ref(null),open=ref(false),positionStyle=ref({})
const route=useRoute()
let unregister=()=>{}
function position(){
  if(!trigger.value||!popover.value)return
  const rect=trigger.value.getBoundingClientRect(),menu=popover.value.getBoundingClientRect(),gap=8,pad=8
  const above=rect.bottom+menu.height+gap>window.innerHeight-pad
  const top=above?Math.max(pad,rect.top-menu.height-gap):Math.min(window.innerHeight-menu.height-pad,rect.bottom+gap)
  const left=Math.max(pad,Math.min(rect.right-menu.width,window.innerWidth-menu.width-pad))
  positionStyle.value={top:`${top}px`,left:`${left}px`}
}
async function activate(){if(open.value){close();return}window.__openPartnershipActionMenu?.();window.__openPartnershipActionMenu=close;open.value=true;await nextTick();position();}
function toggle(){activate()}
function close(){if(!open.value)return;open.value=false;if(window.__openPartnershipActionMenu===close)window.__openPartnershipActionMenu=null}
function outside(event){if(!root.value?.contains(event.target)&&!popover.value?.contains(event.target))close()}
function escape(event){if(event.key==='Escape')close()}
function choose(action){close();emit(action)}
function viewportChange(){if(open.value)close()}
onMounted(()=>{document.addEventListener('click',outside);document.addEventListener('keydown',escape);window.addEventListener('scroll',viewportChange,true);window.addEventListener('resize',viewportChange)})
onBeforeUnmount(()=>{close();document.removeEventListener('click',outside);document.removeEventListener('keydown',escape);window.removeEventListener('scroll',viewportChange,true);window.removeEventListener('resize',viewportChange)})
import { watch } from 'vue'
watch(()=>route.fullPath,close)
</script>
