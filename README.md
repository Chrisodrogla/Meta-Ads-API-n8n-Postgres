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
