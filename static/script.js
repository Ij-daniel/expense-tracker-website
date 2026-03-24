const form = document.getElementById("expense-form");
const expenseList = document.getElementById("expense-list");
const totalDisplay = document.getElementById("total");
const ctx = document.getElementById("expenseChart").getContext("2d");

let chart; // Chart.js instance

// Fetch Expenses
async function fetchExpenses() {
    const res = await fetch('/get_expenses');
    const data = await res.json();

    expenseList.innerHTML = "";
    let total = 0;

    const categoryTotals = {};

    data.forEach(expense => {
        total += expense.amount;

        // Category summary for chart
        if (categoryTotals[expense.category]) {
            categoryTotals[expense.category] += expense.amount;
        } else {
            categoryTotals[expense.category] = expense.amount;
        }

        const li = document.createElement("li");
        li.innerHTML = `
            ${expense.description} (${expense.category}) - ₦${expense.amount}
            <button class="delete-btn" onclick="deleteExpense(${expense.id})">X</button>
        `;
        expenseList.appendChild(li);
    });

    totalDisplay.textContent = total.toFixed(2);

    updateChart(categoryTotals);
}

// Add Expense
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const description = document.getElementById("description").value;
    const amount = parseFloat(document.getElementById("amount").value);
    const category = document.getElementById("category").value;

    await fetch('/add_expense', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ description, amount, category })
    });

    form.reset();
    fetchExpenses();
});

// Delete Expense
async function deleteExpense(id) {
    await fetch(`/delete_expense/${id}`, { method: 'DELETE' });
    fetchExpenses();
}

// Update Chart.js chart
function updateChart(data) {
    const labels = Object.keys(data);
    const values = Object.values(data);

    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Expense by Category',
                data: values,
                backgroundColor: ['#FF6384','#36A2EB','#FFCE56','#4BC0C0','#9966FF','#FF9F40']
            }]
        }
    });
}

// Initial load
fetchExpenses();

function openSidebar() {
    document.getElementById("sidebar").classList.add("show");
}

function closeSidebar() {
    document.getElementById("sidebar").classList.remove("show");
}