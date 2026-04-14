import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:5000/api";

const initialForm = {
  title: "",
  amount: "",
  transaction_type: "expense",
  category: "",
  expense_date: new Date().toISOString().split("T")[0],
  notes: "",
};

function App() {
  const [form, setForm] = useState(initialForm);
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState({
    total_entries: 0,
    total_income: 0,
    total_expense: 0,
    balance: 0,
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadExpenses();
  }, []);

  async function loadExpenses() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/expenses`);
      if (!response.ok) {
        throw new Error("Unable to load transactions.");
      }

      const data = await response.json();
      setExpenses(data.expenses);
      setSummary(data.summary);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/expenses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          amount: Number(form.amount),
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.message || "Unable to save transaction.");
      }

      setForm({
        ...initialForm,
        expense_date: new Date().toISOString().split("T")[0],
      });
      await loadExpenses();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(expenseId) {
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/expenses/${expenseId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || "Unable to delete transaction.");
      }

      await loadExpenses();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function handleReportDownload() {
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/report`);
      if (!response.ok) {
        throw new Error("Unable to generate report.");
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = "expense_report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <div className="page-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Expense Control Dashboard</p>
          <h1>Track income and spending, then export your report in one click.</h1>
          <p className="hero-copy">
            Add every incoming and outgoing transaction, monitor live totals, and generate a clean
            PDF report whenever you need it.
          </p>
        </div>

        <div className="summary-grid">
          <article className="summary-card">
            <span>Total Entries</span>
            <strong>{summary.total_entries}</strong>
          </article>
          <article className="summary-card income-card">
            <span>Total Income</span>
            <strong>Rs. {Number(summary.total_income).toFixed(2)}</strong>
          </article>
          <article className="summary-card highlight">
            <span>Total Expense</span>
            <strong>Rs. {Number(summary.total_expense).toFixed(2)}</strong>
          </article>
          <article className="summary-card balance-card">
            <span>Balance</span>
            <strong>Rs. {Number(summary.balance).toFixed(2)}</strong>
          </article>
        </div>
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-header">
            <h2>Add Transaction</h2>
            <p>Record every expense and income entry with category, amount, and date.</p>
          </div>

          <form className="expense-form" onSubmit={handleSubmit}>
            <label>
              Title
              <input
                name="title"
                value={form.title}
                onChange={updateField}
                placeholder="Groceries or Salary"
                required
              />
            </label>

            <div className="two-column">
              <label>
                Type
                <select name="transaction_type" value={form.transaction_type} onChange={updateField}>
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </label>

              <label>
                Amount
                <input
                  name="amount"
                  value={form.amount}
                  onChange={updateField}
                  type="number"
                  min="0.01"
                  step="0.01"
                  placeholder="0.00"
                  required
                />
              </label>
            </div>

            <label>
              Category
              <input
                name="category"
                value={form.category}
                onChange={updateField}
                placeholder={form.transaction_type === "income" ? "Salary" : "Food"}
                required
              />
            </label>

            <label>
              Date
              <input
                name="expense_date"
                value={form.expense_date}
                onChange={updateField}
                type="date"
                required
              />
            </label>

            <label>
              Notes
              <textarea
                name="notes"
                value={form.notes}
                onChange={updateField}
                rows="4"
                placeholder="Optional details"
              />
            </label>

            <div className="form-actions">
              <button type="submit" disabled={submitting}>
                {submitting ? "Saving..." : "Save Transaction"}
              </button>
              <button type="button" className="secondary" onClick={handleReportDownload}>
                Download PDF Report
              </button>
            </div>
          </form>
        </div>

        <div className="panel">
          <div className="panel-header list-header">
            <div>
              <h2>Transaction History</h2>
              <p>Your latest income and expense entries appear here.</p>
            </div>
            <button type="button" className="ghost-button" onClick={loadExpenses}>
              Refresh
            </button>
          </div>

          {error ? <div className="error-banner">{error}</div> : null}

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Category</th>
                  <th>Date</th>
                  <th>Amount</th>
                  <th>Notes</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="7" className="empty-state">
                      Loading transactions...
                    </td>
                  </tr>
                ) : expenses.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="empty-state">
                      No transactions added yet.
                    </td>
                  </tr>
                ) : (
                  expenses.map((expense) => (
                    <tr key={expense.id}>
                      <td>{expense.title}</td>
                      <td>
                        <span className={`type-pill ${expense.transaction_type}`}>
                          {expense.transaction_type}
                        </span>
                      </td>
                      <td>{expense.category}</td>
                      <td>{expense.expense_date}</td>
                      <td>Rs. {Number(expense.amount).toFixed(2)}</td>
                      <td>{expense.notes || "-"}</td>
                      <td>
                        <button
                          type="button"
                          className="delete-button"
                          onClick={() => handleDelete(expense.id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
