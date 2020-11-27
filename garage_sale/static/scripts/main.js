var cart = {
    total: 0,
    items: []
}

window.addEventListener('load', (event) => {
    // load cookie
    for (let item of JSON.parse(document.cookie.split('cart=')[1])) {
        cart.total += item.cost;
        cart.items.push(item);
    }
    console.log(JSON.stringify(cart));
    document.getElementById('cartButton').addEventListener('click', () => {
        showCart();
    });
    for (let element of document.getElementsByClassName('closesCart')) {
        element.addEventListener('click', () => {
            closeCart();
        });
    }
});

/**
 * Displays the cart on the website
 */
function showCart() {
    populateCartItems();
    document.getElementById('cart').classList.remove('invisible');
    for (let element of document.getElementsByClassName('closesCart')) {
        element.classList.add('blur');
    }
}

function closeCart() {
    document.getElementById('cart').classList.add('invisible');
    for (let element of document.getElementsByClassName('closesCart')) {
        element.classList.remove('blur');
    }
}

/**
 * purchase button callback to add an item to the cart.
 * 
 * Example item json string "{itemName:'somename', cost:0, description: 'some item description', imageDirectory:'/somePath'}"
 * @param {String} iteminfo Json string of product
 */
function purchaseButton(iteminfo) {
    item = JSON.parse(iteminfo);
    addItemToCart(item);
    let cookie = JSON.parse(document.cookie.split('cart=')[1]);
    cookie.push(JSON.parse(iteminfo));
    document.cookie = "cart=" + JSON.stringify(cookie);
}

/**
 * Adds the specified item to the cart  
 * @param {Object} item 
 */
function addItemToCart(item) {
    cart.total += item.cost;
    cart.items.push(item);
    populateCartItems();
}

/**
 * Removes item from the cart 
 * @param {String} itemid itemID being removed
 */
function removeItemFromCart(itemID) {
    for (let i = 0; i < cart.items.length; i++) {
        if (cart.items[i].id == itemID) {
            cart.total -= cart.items[i].cost;
            cart.items.splice(i, 1);
            document.cookie = "cart=" + JSON.stringify(cart.items);
        }
    }
    
    populateCartItems();
}

function populateCartItems() {
    document.getElementById("cartItems").innerHTML = "";
    let html = "";
    for (let item of cart.items) {
        html += `<div class="cartItemContainer container">
            <div class="itemContent">
                <span class="title">${item.name}</span> 
                <span class="cost">$${item.cost}</span>
                <br>
                <span class="description">${item.description}</span>
                <br>
                <span onClick="removeItemFromCart(${item.id})" class="itemRemove">Remove</span>
            </div>
        </div>`;
    }

    document.getElementById("cartItems").innerHTML = html;
    document.getElementById("totalValue").innerHTML = `$${cart.total}`;
}


function resetCookies() {
    let items = [
        {
            "name": "first item",
            "description": "fancy new item",
            "cost": 30,
            "id": 0
        },{
            "name": "second item",
            "description": "not the first item",
            "cost": 45,
            "id": 1
        }
    ]
    document.cookie = "cart=" + JSON.stringify(items);
}