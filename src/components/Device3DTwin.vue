<template>
  <div class="device-3d-container" ref="containerRef">
    <div class="title">3D Digital Twin</div>
    <div class="canvas-box"></div>

    <div class="data-panel">
      <div class="panel-item">Status: <span class="green">Running</span></div>
      <div class="panel-item">Current: {{ data.current }} A</div>
      <div class="panel-item">Speed: {{ data.speed }} r/min</div>
      <div class="panel-item">Wind: {{ data.wind }} m/s</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const containerRef = ref(null)
let scene, camera, renderer, fanGroup, animationId

const data = ref({
  current: 5.6,
  speed: 1200,
  wind: 3.2
})

onMounted(() => {
  init3D()
  animate()
})

function init3D() {
  // 场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0a1629)

  // 相机（透视相机 → 3D 立体关键）
  camera = new THREE.PerspectiveCamera(45, 260 / 220, 0.1, 1000)
  camera.position.set(4, 4, 6)
  camera.lookAt(0, 0, 0)

  // 渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(260, 220)
  renderer.shadowMap.enabled = true
  containerRef.value.querySelector('.canvas-box').appendChild(renderer.domElement)

  // 灯光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0x409eff, 1)
  directionalLight.position.set(5, 10, 7)
  directionalLight.castShadow = true
  scene.add(directionalLight)

  // 设备主体（立体机箱）
  const bodyGeo = new THREE.BoxGeometry(2.2, 2.2, 1.2)
  const bodyMat = new THREE.MeshStandardMaterial({
    color: 0x1890ff,
    metalness: 0.8,
    roughness: 0.2
  })
  const body = new THREE.Mesh(bodyGeo, bodyMat)
  body.castShadow = true
  body.receiveShadow = true
  scene.add(body)

  // 风扇组 → 3D 旋转
  fanGroup = new THREE.Group()
  scene.add(fanGroup)

  // 4叶风扇 → 3D 立体
  const bladeGeo = new THREE.BoxGeometry(0.4, 1.6, 0.2)
  const bladeMat = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.2 })

  for (let i = 0; i < 4; i++) {
    const blade = new THREE.Mesh(bladeGeo, bladeMat)
    blade.rotation.z = (i * Math.PI) / 2
    blade.position.z = 0.8
    fanGroup.add(blade)
  }
}

// 3D 旋转 + 场景自转 → 超强3D感
function animate() {
  animationId = requestAnimationFrame(animate)

  if (fanGroup) {
    fanGroup.rotation.z += 0.05   // 风扇高速旋转
    scene.rotation.y += 0.003     // 设备缓慢自转 → 3D 效果爆炸
  }

  renderer.render(scene, camera)
}

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  renderer?.dispose()
})
</script>

<style scoped>
.device-3d-container {
  width: 280px;
  background: #0b1220;
  border-radius: 12px;
  padding: 14px;
  color: #fff;
  text-align: center;
  border: 1px solid #1979c9;
}

.title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
}

.canvas-box {
  width: 260px;
  height: 220px;
  border-radius: 8px;
  overflow: hidden;
  margin: 0 auto;
}

.data-panel {
  margin-top: 12px;
  font-size: 12px;
  text-align: left;
  background: rgba(255,255,255,0.05);
  padding: 8px 12px;
  border-radius: 6px;
}

.panel-item {
  margin: 4px 0;
}

.green {
  color: #00e078;
  font-weight: bold;
}
</style>