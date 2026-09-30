import { reactive, computed } from 'vue'

const saved = JSON.parse(localStorage.getItem('cart') || '[]')
const savedUser = JSON.parse(localStorage.getItem('user') || 'null')

export const store = reactive({
  cart: saved, // [{product, qty}]
  user: savedUser,
  setUser(u) {
    this.user = u
    localStorage.setItem('user', JSON.stringify(u))
  }
})

export function addToCart(product, qty = 1) {
  const line = store.cart.find(l => l.product.id === product.id)
  if (line) line.qty += qty
  else store.cart.push({ product, qty })
  persist()
}

export function removeFromCart(productId) {
  store.cart = store.cart.filter(l => l.product.id !== productId)
  persist()
}

export function setQty(productId, qty) {
  const line = store.cart.find(l => l.product.id === productId)
  if (line) line.qty = Math.max(1, qty)
  persist()
}

export function clearCart() {
  store.cart = []
  persist()
}

function persist() {
  localStorage.setItem('cart', JSON.stringify(store.cart))
}

export const cartTotal = computed(() =>
  store.cart.reduce((s, l) => s + Number(l.product.price) * l.qty, 0)
)
export const cartCount = computed(() => store.cart.reduce((s, l) => s + l.qty, 0))
