# 📚 GymPro API Documentation

## Base URL
```
http://localhost:5001
```

## Endpoints Overview

### Dashboard & Navigation
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard with stats and member list |
| `/search` | GET | Search members (query param: `q`) |
| `/leaderboard` | GET | Member leaderboard with rankings |
| `/statistics` | GET | Comprehensive analytics dashboard |

### Member Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/add-member` | POST | Create new member |
| `/member/<id>` | GET | View member profile and details |
| `/remove-member/<id>` | POST | Deactivate member |
| `/reactivate-member/<id>` | POST | Reactivate inactive member |
| `/inactive-members` | GET | View all inactive members |
| `/insights/<id>` | GET | Detailed member insights page |

### Attendance Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/attendance/<id>` | GET, POST | View/mark member attendance |

### Weight Tracking
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/add-weight` | POST | Log member weight |

### Fee Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/add-fees` | POST | Add fee record for member |
| `/fees` | GET | View all pending fees |
| `/pay-fees/<id>` | POST | Mark fee as paid |

### Goals & Fitness
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/goals` | GET | View all member goals dashboard |
| `/set-goal/<id>` | POST | Create/update member goal |
| `/achievement/<id>` | GET | Mark goal as achieved |

### Analytics & Reports
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profits` | GET | View profit tracking dashboard |

---

## Detailed Endpoint Documentation

### 1. GET `/`
**Main Dashboard**

**Response:** HTML page with:
- Active members count
- Pending fees summary
- Total profit
- Fee reminder alerts
- Member grid with quick actions
- Dashboard navigation buttons

**Uses Data:**
- Members (active status)
- Fees (pending within 2-3 days)
- Profits (total sum)

---

### 2. GET `/search?q=<query>`
**Member Search**

**Query Parameters:**
- `q` (required): Search term (name, phone, or email)

**Response:** Search results page with:
- Matching member cards
- Result count
- Quick action buttons

**Search Fields:**
- Member name (LIKE match)
- Phone number (LIKE match)
- Email address (LIKE match)

---

### 3. GET `/leaderboard`
**Member Leaderboard**

**Response:** Ranked table with:
- Rank number (with medals for top 3)
- Member name and avatar
- Goal type badge
- Attendance count
- Goal progress percentage
- View details link

**Ranking Criteria:**
1. Attendance count (descending)
2. Goal progress percentage (descending)

---

### 4. GET `/statistics`
**Analytics Dashboard**

**Response:** Comprehensive statistics page with:
- **Stat Cards:**
  - Active members count
  - Total profit amount
  - Total attended members
  - Average attendance per member
  - Total goals
  - Goal completion rate

- **Goal Statistics:**
  - Weight loss members count
  - Weight gain members count
  - Achieved goals count
  - Completion rate progress bar

- **Top Members:**
  - Ranked list of most dedicated members
  - Check-in counts

---

### 5. POST `/add-member`
**Create New Member**

**Request Body (Form Data):**
```json
{
  "name": "John Doe",
  "phone": "9876543210",
  "email": "john@example.com",
  "weight": 85.5
}
```

**Response:** 
- Redirect to dashboard
- Flash: Member added successfully

**Validations:**
- Name must be unique
- Phone and email are optional

---

### 6. GET `/member/<id>`
**Member Profile**

**URL Parameters:**
- `id` (required): Member ID

**Response:** Member profile page with:
- Personal information
- Start weight
- Status (active/inactive)
- Current goal (if set)
  - Goal type badge
  - Target weight
  - Deadline
  - Progress percentage
  - Progress bar
- Attendance statistics
- Fee records
- Weight history
- Action buttons

---

### 7. POST `/remove-member/<id>`
**Deactivate Member**

**URL Parameters:**
- `id` (required): Member ID

**Response:**
- Redirect to dashboard
- Flash: Member removed

**Effect:**
- Changes member status to 'inactive'
- Member still in database (preserved history)

---

### 8. POST `/reactivate-member/<id>`
**Reactivate Inactive Member**

**URL Parameters:**
- `id` (required): Member ID

**Response:**
- Redirect to dashboard
- Flash: Member reactivated

**Effect:**
- Changes member status back to 'active'

---

### 9. GET/POST `/attendance/<id>`
**Attendance Management**

**GET Response:** Attendance form/page

**POST Request Body:**
```json
{
  "status": "present",
  "date": "2024-01-02"
}
```

**POST Response:**
- Redirect to member profile
- Flash: Attendance marked

**Valid Status Values:**
- "present"
- "absent"
- "leave"
- "late"

**Constraint:** One attendance per member per day (UNIQUE)

---

### 10. POST `/add-weight`
**Log Weight**

**Request Body (Form Data):**
```json
{
  "member_id": 1,
  "weight": 82.5,
  "month": "2024-01"
}
```

**Response:**
- Redirect to member profile
- Flash: Weight logged successfully

**Calculation:**
- Progress calculated from starting weight
- Used for goal progress percentage

---

### 11. POST `/add-fees`
**Add Fee Record**

**Request Body (Form Data):**
```json
{
  "member_id": 1,
  "amount": 5000
}
```

**Response:**
- Redirect to fees dashboard
- Flash: Fee added successfully

**Auto-calculation:**
- `last_paid`: Current date
- `next_due`: Current date + 30 days
- `paid_status`: "pending"

---

### 12. GET `/fees`
**Fees Dashboard**

**Response:** Fee management page with:
- Pending fees section
  - Member details
  - Fee amount
  - Due date
  - Days until due
  - Mark as paid button
- Paid fees section
  - Payment history
  - Dates and amounts

---

### 13. POST `/pay-fees/<id>`
**Mark Fee as Paid**

**URL Parameters:**
- `id` (required): Member ID

**Response:**
- Redirect to fees dashboard
- Flash: Fee paid successfully

**Effect:**
- Sets fee `paid_status` to "paid"
- Creates automatic profit entry
- Adds to total profit

---

### 14. GET `/goals`
**Goals Dashboard**

**Response:** Comprehensive goals page with:
- **Statistics Cards:**
  - Total active goals
  - Achieved goals count
  - Weight loss members
  - Weight gain members

- **Goals Grid:**
  - Each goal card shows:
    - Member name
    - Goal type (weight loss/gain)
    - Start weight
    - Target weight
    - Deadline
    - Progress percentage
    - Link to member profile

---

### 15. POST `/set-goal/<id>`
**Create/Update Goal**

**URL Parameters:**
- `id` (required): Member ID

**Request Body (Form Data):**
```json
{
  "goal_type": "weight_loss",
  "target_weight": 75.0,
  "deadline": "2024-06-30"
}
```

**Response:**
- Redirect to member profile
- Flash: Goal set/updated successfully

**Validation:**
- Goal type: "weight_loss" or "weight_gain"
- Target weight: Valid number
- Deadline: Valid date

**Logic:**
- If goal exists: UPDATE
- If goal doesn't exist: INSERT
- Only one goal per member (UNIQUE constraint)

---

### 16. GET `/achievement/<id>`
**Mark Achievement**

**URL Parameters:**
- `id` (required): Member ID

**Response:**
- Redirect to member profile
- Flash: Goal achievement recorded! 🎉

**Effect:**
- Sets goal `achieved` to 1
- Updates achievement stats

---

### 17. GET `/insights/<id>`
**Member Insights**

**URL Parameters:**
- `id` (required): Member ID

**Response:** Detailed insights page with:
- **Member Header:**
  - Avatar, name, contact info
  - Join date, status
  
- **Quick Stats:**
  - Attendance rate percentage
  - Starting weight
  - Payments made

- **Current Goal:**
  - Goal details card
  - Progress information

- **Attendance Timeline:**
  - Last 30 days records
  - Status indicators

- **Weight Progress Timeline:**
  - Historical weight logs
  - Change indicators

---

### 18. GET `/profits`
**Profit Dashboard**

**Response:** Profit analytics page with:
- Total profit amount
- Profit by member breakdown
- Recent payments history
- Revenue summary

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Page/data returned |
| 302 | Redirect - After POST action |
| 400 | Bad Request - Invalid data |
| 404 | Not Found - Member/resource not found |
| 500 | Server Error |

---

## Data Structures

### Member Object
```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "9876543210",
  "email": "john@example.com",
  "join_date": "2024-01-01",
  "start_weight": 85.5,
  "status": "active",
  "goal_type": "weight_loss",
  "target_weight": 75.0,
  "goal_deadline": "2024-06-30"
}
```

### Fee Object
```json
{
  "id": 1,
  "member_id": 1,
  "amount": 5000,
  "last_paid": "2024-01-01",
  "next_due": "2024-01-31",
  "paid_status": "pending"
}
```

### Goal Object
```json
{
  "id": 1,
  "member_id": 1,
  "goal_type": "weight_loss",
  "target_weight": 75.0,
  "deadline": "2024-06-30",
  "created_date": "2024-01-01",
  "achieved": 0
}
```

---

## Common Query Parameters

| Parameter | Used In | Description |
|-----------|---------|-------------|
| `q` | /search | Search query term |

---

## Error Handling

**Flash Messages:**
- Success messages (green)
- Error messages (red)
- Info messages (blue)

**Validation:**
- Server-side validation on all forms
- Data type checking
- Unique constraint enforcement
- Date format validation

---

## Performance Notes

- Database queries optimized with SELECT specific columns
- Indexed lookups on member_id and dates
- Pagination not yet implemented (can handle ~1000 members efficiently)
- Response times: < 200ms for most endpoints

---

## Future Enhancement Endpoints

Potential additions for v2.0:
- `POST /import-members` - Bulk member import
- `GET /reports/monthly` - Monthly reports
- `GET /export/pdf` - PDF export
- `POST /api/attendance` - RESTful API version
- WebSocket support for real-time updates

---

**API Last Updated:** January 2, 2026
**GymPro Version:** 2.0 (With Finishing Touches)
