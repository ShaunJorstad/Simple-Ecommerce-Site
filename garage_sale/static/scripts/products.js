document.addEventListener("DOMContentLoaded", function(){

    let loadBtn = document.getElementById("load-btn");

    loadBtn.addEventListener("click", loadProducts);
});

function loadProducts(){
    let allProd = document.getElementsByClassName("product");
    let lastProd = allProd.item(allProd.length - 1);
    let prod_num = lastProd.id

    fetch("/fetchproducts/" + prod_num).then(function(response){
        if (response.ok) {return response.json();}
        else {return Promise.reject(response);}
    }).then(insertProducts)
}

function insertProducts(prods){
    let container = document.getElementById("prod-container")
    for(let product of prods){
        //image
        let img = document.createElement('img');
        img.className = "prodImg";
        //this doesnt account for no images
        img.src = "/static/images/products/" + product[5];
        img.alt = "product image";

        //div that wraps the image
        let imgWrap = document.createElement('div');
        imgWrap.className = "product-image";
        imgWrap.appendChild(img);

        //Title
        let title = document.createElement('h3');
        let text = document.createTextNode("" + product[1]);
        title.appendChild(text);

        //price
        let price = document.createElement('p');
        let pText = document.createTextNode("$" + product[2]);
        price.appendChild(pText);

        //link that wraps everything above
        let link = document.createElement('a');
        link.href = "/products/" + product[0];
        
        //embed all the documents into link
        link.appendChild(imgWrap);
        link.appendChild(title);
        link.appendChild(price);

        //the final product element
        let e = document.createElement('div');
        e.className = "product";
        e.id = product[0];
        e.appendChild(link);
        
        //add the product to the page
        container.appendChild(e);
    }
}
