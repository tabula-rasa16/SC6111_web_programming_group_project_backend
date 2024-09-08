document.addEventListener("DOMContentLoaded", function () {

  // Fetch Order Book data for both Buy and Sell orders
  fetchBuyOrders();
  fetchSellOrders();
});

function calculateTotal() {
  var price = parseFloat(document.getElementById("price").value);
  var amount = parseFloat(document.getElementById("amount").value);
  var total = price * amount;
  document.getElementById("total").innerText = total.toFixed(2);
}

function buy() {
  alert("Buy action triggered");
}

function sell() {
  alert("Sell action triggered");
}

function fetchBuyOrders() {
  $.ajax({
    url: "/api/order-book/buy", // Replace with your actual API endpoint
    type: "GET",
    success: function (data) {
      const buyList = data.buyOrders || [];
      const buyOrdersDiv = document.getElementById("buyOrders");

      buyOrdersDiv.innerHTML = ""; // Clear previous content

      if (buyList.length === 0) {
        buyOrdersDiv.innerHTML = "<div>No Buy Orders</div>";
      } else {
        buyList.forEach((order) => {
          buyOrdersDiv.innerHTML += `
            <div class="order-book">
              <span>${order.price}</span>
              <span>${order.amount}</span>
            </div>`;
        });
      }
    },
    error: function () {
      document.getElementById("buyOrders").innerHTML =
        "<div>Error loading Buy Orders</div>";
    },
  });
}

function fetchSellOrders() {
  $.ajax({
    url: "/api/order-book/sell", // Replace with your actual API endpoint
    type: "GET",
    success: function (data) {
      const sellList = data.sellOrders || [];
      const sellOrdersDiv = document.getElementById("sellOrders");

      sellOrdersDiv.innerHTML = ""; // Clear previous content

      if (sellList.length === 0) {
        sellOrdersDiv.innerHTML = "<div>No Sell Orders</div>";
      } else {
        sellList.forEach((order) => {
          sellOrdersDiv.innerHTML += `
            <div class="order-book">
              <span>${order.price}</span>
              <span>${order.amount}</span>
            </div>`;
        });
      }
    },
    error: function () {
      document.getElementById("sellOrders").innerHTML =
        "<div>Error loading Sell Orders</div>";
    },
  });
}
