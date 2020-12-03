
var cart = {
  total: 0,
  items: [],
};

var cartOpen = false;

window.addEventListener('load', (event) => {
  // load cookie
  for (let item of JSON.parse(getCookie())) {
    cart.total += item.cost;
    cart.items.push(item);
  }
  console.log(JSON.stringify(cart));
  document.getElementById('cartButton').addEventListener('click', () => {
    if (cartOpen) {
      closeCart();
    } else {
      showCart();
    }
  });

  for (let element of document.getElementsByClassName('closesCart')) {
    element.addEventListener('click', closeCart);
  }
}
);

window.addEventListener("DOMContentLoaded", function () {

  var stripe = Stripe(
    "pk_test_51HtJ0uDZJqO6LNTXLVst87QQozp70xOS8yhlzphc17W8yF379FeBwcTYifK6a4EDShQTGo8odZBdmsedpptiu2fW007lkc8zXO"
  );
  let checkoutButton = document.getElementById("cartPurchaseButton");

  checkoutButton.addEventListener("click", function () {
    // Create a new Checkout Session using the server-side endpoint you
    // created in step 3.
    var data = new FormData();

    data.append("length", cart.items.length);
    for (var i = 0; i < cart.items.length; i++) {
      var current = cart.items[i];
      data.append("name" + i, current.name);
      data.append("description" + i, current.description);
      data.append("price" + i, current.cost);
    }
    fetch("/create-checkout-session", {
      method: "POST",
      body: data
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (session) {
        return stripe.redirectToCheckout({ sessionId: session.id });
      })
      .then(function (result) {
        // If `redirectToCheckout` fails due to a browser or network
        // error, you should display the localized error message to your
        // customer using `error.message`.
        if (result.error) {
          alert(result.error.message);
        }
      })
      .catch(function (error) {
        console.error("Error:", error);
      });
  });
});

function getCookie() {
  if (!document.cookie.includes("cart")) {
    document.cookie = "cart=[];path=/";
  }
  return document.cookie.split('cart=')[1];
}

function setCookie(contents) {
  document.cookie = `cart=${contents};path=/`;
}

/**
 * Displays the cart on the website
 */
function showCart() {
  populateCartItems();
  document.getElementById('cart').classList.remove('invisible');
  for (let element of document.getElementsByClassName('closesCart')) {
    element.classList.add('blur');
  }
  cartOpen = true;
}

function closeCart() {
  document.getElementById('cart').classList.add('invisible');
  for (let element of document.getElementsByClassName('closesCart')) {
    element.classList.remove('blur');
  }
  cartOpen = false;
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
  let cookie = JSON.parse(getCookie());
  cookie.push(JSON.parse(iteminfo));
  setCookie(JSON.stringify(cookie));
}

function addProductToCart(name, cost, description) {
  product = {
    "name": name,
    "cost": cost,
    "description": description
  }
  addItemToCart(product);
  let cookie = JSON.parse(getCookie());
  console.log("current cookie" + cookie);
  cookie.push(product);
  setCookie(JSON.stringify(cookie));
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
      setCookie(JSON.stringify(cart.items));
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
      name: "first item",
      description: "fancy new item",
      cost: 30,
      id: 0,
    },
    {
      name: "second item",
      description: "not the first item",
      cost: 45,
      id: 1,
    },
  ];
  setCookie(JSON.stringify(items));
}
