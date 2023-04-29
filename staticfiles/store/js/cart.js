var updateBtns = document.getElementsByClassName('update-cart')

for(var i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action

        // console.log(productId, action)
        // console.log(user)

        if(user === 'AnonymousUser'){
            addCookieItem(productId, action)
        }
        else{
            updateUserOrder(productId, action)
        }
    })
}

function addCookieItem(productId, action){
    console.log("You are not logged in...")

    if(action == 'add'){
        if(cart[productId] == undefined){
            cart[productId] = 1
        }
        else{
            cart[productId] += 1
        }
    }

    if(action == 'remove'){
        cart[productId] -= 1

        if(cart[productId] <= 0){
            console.log("Order item deleted")
            delete cart[productId]
        }
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    console.log("Cart; ", cart)
    location.reload()
}

function updateUserOrder(productId, action){
    console.log("I know you...")

    var url = '/update_item/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken
        },
        body:JSON.stringify({
            'productId': productId,
            'action': action
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data)
        // location.reload()
        document.getElementById('total-quantity').innerHTML = data['qty']['qty']
    })
}
