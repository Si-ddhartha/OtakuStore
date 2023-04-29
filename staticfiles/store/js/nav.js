const toggleButton = document.getElementsByClassName('toggle-button')[0]
const navGroup = document.getElementsByClassName('nav-group')[0]

toggleButton.addEventListener('click', () =>{
    navGroup.classList.toggle('active')
})