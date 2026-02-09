# 📊 Meta Ads Campaign Insights Workflow

Automated workflow that retrieves **Meta Ads campaign data**, collects performance metrics, filters incomplete records, and stores the cleaned results in a **PostgreSQL (Supabase)** database.

---

## ⚙️ Workflow Overall Process

### 🔎 1. Observe Specific Ad Account ID
This workflow retrieves campaigns only from the ad account:

`act_1222178640101234`

Multiple ad accounts can be monitored, but this example uses a single account.

---

### 📋 2. Get Campaign List Under Ad Account ID
An API request fetches the list of campaigns under the selected ad account, including:

- `campaign_name`
- `campaign_id`

---

### 📈 3. Get Insights / Metrics for Each Campaign
A looped API request retrieves campaign performance metrics such as:

- `spend`
- `impressions`
- `clicks`
- `date_start`
- `date_stop`
- other available metrics if needed

---

### 🚫 4. Handle Null Insight and Metric Values
A **Filter node** removes campaigns where **date_start** is `null`, which usually means the campaign has not yet been published or insights are not available.

**Example (Filtered Campaign)**

```json
{
  "campaign_id": "120242418331871234",
  "campaign_name": "Campaign with null Insights",
  "spend": null,
  "impressions": null,
  "clicks": null,
  "date_start": null,
  "date_stop": null
}
```

## 🗄️ 5. Append to PostgreSQL Database (Supabase)

After collecting and cleaning the data, the workflow executes an SQL query to append the results to the existing PostgreSQL table hosted in Supabase.

**PostgreSQL Table Fields**
- `id` – Primary key used to uniquely identify each appended record  
- `date_added` – Timestamp indicating when the record was inserted  

**Example Stored Record**

```json
{
  "id": 1,
  "campaign_id": "12024123121231234",
  "campaign_name": "Learn Python with our Course",
  "spend": "10.5",
  "impressions": "1234",
  "clicks": "10",
  "account_id": "11112222333344",
  "date_start": "2026-02-07",
  "date_stop": "2026-02-09",
  "date_added": "2026-02-09T10:50:15Z"
}
```