document.addEventListener("DOMContentLoaded", function () {
  console.log("Fetching order list...");
  fetchOrderList();
  console.log("Fetching trade list...");
  fetchTradeList();
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

function fetchOrderList() {
  $.ajax({
    url: "/getOrderList", // Single API endpoint
    type: "GET",
    success: function (data) {
      if (data.code === 200) {
        const buyList = data.data.buyList || [];
        const sellList = data.data.sellList || [];

        // Clear and update buy orders
        const buyOrdersDiv = document.getElementById("buyOrders");
        buyOrdersDiv.innerHTML = ""; // Clear previous content
        if (buyList.length === 0) {
          buyOrdersDiv.innerHTML = "<div>No Buy Orders</div>";
        } else {
          buyList.forEach((order) => {
            buyOrdersDiv.innerHTML += `
              <div class="order-book-item">
                <span>${order.price}</span>
                <span>${order.amount}</span>
              </div>`;
          });
        }

        // Clear and update sell orders
        const sellOrdersDiv = document.getElementById("sellOrders");
        sellOrdersDiv.innerHTML = ""; // Clear previous content
        if (sellList.length === 0) {
          sellOrdersDiv.innerHTML = "<div>No Sell Orders</div>";
        } else {
          sellList.forEach((order) => {
            sellOrdersDiv.innerHTML += `
              <div class="order-book-item">
                <span>${order.price}</span>
                <span>${order.amount}</span>
              </div>`;
          });
        }

        // Update middle price with the highest buy price
        const highestBuyPrice = data.data.maxBuyPrice;
        document.getElementById("middlePrice").innerHTML =
          highestBuyPrice.toFixed(2);
      } else {
        console.error("Error fetching order list: " + data.message);
      }
    },
    error: function (xhr, status, error) {
      console.error("Failed to fetch order list: " + error);

      // Handle error by displaying placeholders for buy and sell orders
      document.getElementById("buyOrders").innerHTML =
        "<div>Error loading Buy Orders</div>";
      document.getElementById("sellOrders").innerHTML =
        "<div>Error loading Sell Orders</div>";
      document.getElementById("middlePrice").innerHTML = "N/A";
    },
  });
}

function fetchTradeList() {
  $.ajax({
    url: "/getTradeList",
    type: "GET",
    success: function (data) {
      if (data.code === 200) {
        const tradeList = data.data.tradeList || [];

        // Clear and update trade list
        const tradeListDiv = document.getElementById("marketTradeList");
        tradeListDiv.innerHTML = ""; // Clear previous content

        if (tradeList.length === 0) {
          tradeListDiv.innerHTML = "<div>No Trades Available</div>";
        } else {
          tradeList.forEach((trade) => {
            tradeListDiv.innerHTML += `
              <div class="right-item">
                <span>${trade.price}</span>
                <span>${trade.amount}</span>
                <span>${trade.create_time}</span>
              </div>`;
          });
        }
      } else {
        console.error("Error fetching trade list: " + data.message);
      }
    },
    error: function (xhr, status, error) {
      console.error("Failed to fetch trade list: " + error);

      // Handle error by displaying a placeholder
      document.getElementById("marketTradeList").innerHTML =
        "<div>Error loading Trade List</div>";
    },
  });
}

