const toggleOrderSummary = document.getElementsByClassName('toggle-order-summary')[0]
const col2 = document.getElementsByClassName('col2')[0]

toggleOrderSummary.addEventListener('click', () =>{
    col2.classList.toggle('active')
})