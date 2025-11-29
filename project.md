# FitMates V2 - Project Workflow

## Overview

A comprehensive fitness client management system with role-based access (Admin & User), dynamic form builder, and automated reporting capabilities.

## Tech Stack

- **Backend**: Python, FastAPI, asyncpg
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Database**: PostgreSQL
- **Authentication**: JWT-based authentication

---

## Database Schema

### Tables Structure

```sql
-- Admins Table
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clients Table
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    dob DATE,
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    mobile VARCHAR(20),
    medical_history VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forms Table
CREATE TABLE forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    is_template BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- History/Submissions Table
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    form_id UUID REFERENCES forms(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports Table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    submission_id UUID REFERENCES submissions(id) ON DELETE CASCADE,
    generated_report_data JSONB NOT NULL,
    period VARCHAR(20) CHECK (period IN ('weekly', 'monthly')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Implementation Workflow

### Phase 1: Project Setup & Database Configuration

#### 1.1 Initialize Project Structure

```
FitMates-V2/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── client.py
│   │   ├── form.py
│   │   ├── submission.py
│   │   └── report.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── client.py
│   │   ├── forms.py
│   │   └── reports.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── password.py
│   │   └── report_generator.py
│   └── requirements.txt
├── frontend/
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── clients.html
│   │   ├── client-profile.html
│   │   └── assets/
│   │       ├── css/
│   │       │   └── admin.css
│   │       └── js/
│   │           ├── dashboard.js
│   │           ├── clients.js
│   │           └── client-profile.js
│   ├── user/
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   └── assets/
│   │       ├── css/
│   │       │   └── user.css
│   │       └── js/
│   │           ├── dashboard.js
│   │           └── profile.js
│   ├── shared/
│   │   ├── login.html
│   │   └── assets/
│   │       ├── css/
│   │       │   └── common.css
│   │       └── js/
│   │           ├── auth.js
│   │           └── api.js
│   └── index.html
└── project.md
```

#### 1.2 Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install fastapi uvicorn asyncpg python-jose[cryptography] passlib[bcrypt] python-multipart pydantic-settings
pip freeze > backend/requirements.txt
```

#### 1.3 Setup PostgreSQL Database

```bash
# Create database
createdb fitmates_v2

# Run schema creation script
psql -d fitmates_v2 -f schema.sql
```

---

### Phase 2: Backend Development

#### 2.1 Database Connection (`backend/database.py`)

- Configure asyncpg connection pool
- Create database connection manager
- Implement connection lifecycle (startup/shutdown)

#### 2.2 Configuration (`backend/config.py`)

- Database credentials
- JWT secret key and algorithm
- CORS settings
- Environment variables

#### 2.3 Authentication Utilities (`backend/utils/`)

- **`password.py`**: Password hashing and verification (bcrypt)
- **`auth.py`**: JWT token creation and validation
- Role-based access control decorators

#### 2.4 API Routes Implementation

##### 2.4.1 Authentication Routes (`backend/routes/auth.py`)

- `POST /api/auth/login` - Login for both admin and clients
  - Verify credentials
  - Return JWT token with role (admin/client)
  - Return user details
- `POST /api/auth/register-client` - Client self-registration (optional)
- `GET /api/auth/verify` - Verify JWT token

##### 2.4.2 Admin Routes (`backend/routes/admin.py`)

- `GET /api/admin/dashboard/analytics` - Dashboard analytics
  - Total clients count
  - Forms published count
  - Submissions count
  - Recent activity
- `GET /api/admin/clients` - List all clients
- `GET /api/admin/clients/{client_id}` - Get client details
- `POST /api/admin/clients` - Create new client
- `PUT /api/admin/clients/{client_id}` - Update client details
- `DELETE /api/admin/clients/{client_id}` - Delete client

##### 2.4.3 Forms Routes (`backend/routes/forms.py`)

- `GET /api/forms/client/{client_id}` - Get all forms for a client
- `POST /api/forms` - Create new form (draft)
  - Store custom table structure in JSONB
- `PUT /api/forms/{form_id}` - Edit form
- `POST /api/forms/{form_id}/save` - Save form as draft
- `POST /api/forms/{form_id}/publish` - Publish form to client
- `POST /api/forms/{form_id}/copy` - Copy form (create template)
- `DELETE /api/forms/{form_id}` - Delete form
- `GET /api/forms/templates` - Get all templates (is_template=true)

##### 2.4.4 Submissions Routes (`backend/routes/forms.py`)

- `GET /api/submissions/client/{client_id}` - Get client submissions
- `POST /api/submissions` - Submit form data (client side)
- `GET /api/submissions/{submission_id}` - Get submission details

##### 2.4.5 Reports Routes (`backend/routes/reports.py`)

- `GET /api/reports/client/{client_id}` - Get all reports for client
- `POST /api/reports/generate` - Generate report from submission
  - Compare user data with admin targets
  - Calculate progress/variance
  - Store in reports table
- `GET /api/reports/{report_id}` - Get specific report

#### 2.5 Report Generation Logic (`backend/utils/report_generator.py`)

- Parse form data (targets from admin)
- Parse submission data (actuals from client)
- Calculate metrics:
  - Achievement percentage
  - Variance analysis
  - Trend analysis (if historical data available)
- Generate formatted report (JSON structure)

#### 2.6 Main Application (`backend/main.py`)

- Initialize FastAPI app
- Configure CORS
- Register all routes
- Setup database connection on startup
- Serve static files (frontend)

---

### Phase 3: Frontend Development

#### 3.1 Shared Components

##### 3.1.1 Login Page (`frontend/shared/login.html`)

- Email and password inputs
- Login button
- Role detection (admin vs client based on credentials)
- Redirect to appropriate dashboard

##### 3.1.2 Common Utilities (`frontend/shared/assets/js/`)

- **`api.js`**: API call wrapper functions
  - Handle authentication headers
  - Error handling
  - Base URL configuration
- **`auth.js`**: Authentication utilities
  - Store/retrieve JWT token (localStorage)
  - Check authentication status
  - Logout functionality
  - Role-based redirects

##### 3.1.3 Common Styles (`frontend/shared/assets/css/common.css`)

- CSS variables for theming
- Typography
- Form elements
- Buttons
- Cards
- Tables
- Modals

---

#### 3.2 Admin Frontend

##### 3.2.1 Admin Dashboard (`frontend/admin/dashboard.html`)

**Features:**

- Analytics cards:
  - Total clients
  - Active forms
  - Pending submissions
  - Recent reports
- Charts/graphs (optional - can use Chart.js)
- Recent activity feed

**JavaScript (`dashboard.js`):**

- Fetch analytics data from API
- Render statistics
- Auto-refresh functionality

##### 3.2.2 Clients List (`frontend/admin/clients.html`)

**Features:**

- Grid/list of client cards
- Each card displays:
  - Client ID
  - Name
  - Email
  - Age (calculated from DOB)
  - Height
  - Weight
- Search/filter functionality
- Click to view client profile

**JavaScript (`clients.js`):**

- Fetch all clients
- Render client cards
- Handle card click → navigate to client profile
- Search/filter logic

##### 3.2.3 Client Profile/Details (`frontend/admin/client-profile.html`)

**Layout:**

- Header: Client basic info
- Two tabs: Forms | Reports

**Forms Tab:**

- Table view of all forms for this client
- Columns: Form Title | Status | Created | Actions
- Actions:
  - **Edit**: Open form builder modal
  - **Save**: Save as draft
  - **Publish**: Publish to client
  - **Copy**: Create template from form
- "Create New Form" button

**Form Builder Modal:**

- Dynamic table creator
- Add/remove rows and columns
- Set field types (text, number, date, etc.)
- Set target values
- Save as JSONB structure

**Reports Tab:**

- List of generated reports
- Filter by period (weekly/monthly)
- View report details
- Download/print functionality

**JavaScript (`client-profile.js`):**

- Fetch client details
- Tab switching logic
- Form CRUD operations
- Form builder functionality
- Dynamic table generation
- API calls for forms and reports

---

#### 3.3 User/Client Frontend

##### 3.3.1 User Dashboard (`frontend/user/dashboard.html`)

**Features:**

- Published forms section
  - Display forms sent by admin
  - Fill form functionality
  - Submit button
- Reports section
  - View generated reports
  - Filter by period
  - Visual representation of progress

**JavaScript (`user/dashboard.js`):**

- Fetch published forms for logged-in client
- Render forms with input fields
- Handle form submission
- Fetch and display reports

##### 3.3.2 User Profile (`frontend/user/profile.html`)

**Features:**

- Display user details (editable)
  - Name
  - Email
  - DOB
  - Height
  - Weight
  - Mobile
  - Medical history
- Edit mode toggle
- Save button
- Password change option

**JavaScript (`user/profile.js`):**

- Fetch client profile
- Enable/disable edit mode
- Update profile API call
- Real-time validation

---

### Phase 4: Integration & Features

#### 4.1 Authentication Flow

1. User enters credentials on login page
2. Backend validates and returns JWT + role
3. Frontend stores token in localStorage
4. Redirect based on role:
   - Admin → `/admin/dashboard.html`
   - Client → `/user/dashboard.html`
5. All subsequent API calls include JWT in Authorization header
6. Backend middleware validates token and role

#### 4.2 Form Builder Implementation

**Data Structure (JSONB):**

```json
{
  "title": "Weekly Fitness Plan",
  "fields": [
    {
      "id": "field_1",
      "label": "Cardio Minutes",
      "type": "number",
      "target": 150,
      "unit": "minutes"
    },
    {
      "id": "field_2",
      "label": "Weight Training Sessions",
      "type": "number",
      "target": 3,
      "unit": "sessions"
    }
  ]
}
```

**Frontend:**

- Dynamic form builder UI
- Add/remove fields
- Set field properties
- Preview mode

#### 4.3 Form Submission & Validation

**Client Side:**

- Render form based on JSONB structure
- Validate inputs
- Submit to API

**Backend:**

- Store submission in submissions table
- Link to form_id and client_id

#### 4.4 Report Generation

**Trigger:** After form submission
**Process:**

1. Fetch form data (targets)
2. Fetch submission data (actuals)
3. Calculate metrics:
   ```javascript
   achievement = (actual / target) * 100;
   variance = actual - target;
   ```
4. Generate report JSON:
   ```json
   {
     "period": "weekly",
     "metrics": [
       {
         "field": "Cardio Minutes",
         "target": 150,
         "actual": 140,
         "achievement": 93.33,
         "variance": -10
       }
     ],
     "overall_score": 90,
     "summary": "Good progress, slightly below target on cardio"
   }
   ```
5. Store in reports table

#### 4.5 Real-time Data Sync

- When client updates profile, changes reflect in admin view
- Use timestamp-based updates
- Implement optimistic UI updates

---

### Phase 5: Styling & UX

#### 5.1 Design System

- Color palette (primary, secondary, accent)
- Typography scale
- Spacing system
- Component library

#### 5.2 Responsive Design

- Mobile-first approach
- Breakpoints: 320px, 768px, 1024px, 1440px
- Flexible grid system

#### 5.3 Animations & Interactions

- Page transitions
- Loading states
- Success/error notifications
- Hover effects
- Smooth scrolling

#### 5.4 Accessibility

- ARIA labels
- Keyboard navigation
- Focus states
- Color contrast compliance

---

### Phase 6: Testing & Validation

#### 6.1 Backend Testing

- Test all API endpoints with Postman/Thunder Client
- Validate authentication flow
- Test CRUD operations
- Verify JSONB data integrity
- Test report generation logic

#### 6.2 Frontend Testing

- Test all user flows:
  - Admin login → dashboard → clients → client profile → forms → reports
  - Client login → dashboard → fill form → view reports → edit profile
- Cross-browser testing
- Responsive design testing
- Form validation testing

#### 6.3 Integration Testing

- End-to-end user scenarios
- Data consistency checks
- Error handling validation

---

### Phase 7: Deployment Preparation

#### 7.1 Environment Configuration

- Production database setup
- Environment variables
- CORS configuration for production domain

#### 7.2 Security Hardening

- HTTPS enforcement
- SQL injection prevention (parameterized queries)
- XSS protection
- CSRF tokens (if needed)
- Rate limiting

#### 7.3 Performance Optimization

- Database indexing
- Query optimization
- Frontend asset minification
- Lazy loading
- Caching strategies

#### 7.4 Documentation

- API documentation (Swagger/OpenAPI)
- User manual
- Admin guide
- Deployment guide

---

## Development Checklist

### Backend

- [ ] Setup project structure
- [ ] Configure database connection
- [ ] Implement authentication system
- [ ] Create admin routes
- [ ] Create client routes
- [ ] Create forms routes
- [ ] Create submissions routes
- [ ] Create reports routes
- [ ] Implement report generation logic
- [ ] Add error handling
- [ ] Add logging

### Frontend - Admin

- [ ] Create login page
- [ ] Create admin dashboard
- [ ] Create clients list page
- [ ] Create client profile page
- [ ] Implement form builder
- [ ] Implement form management (edit, save, publish, copy)
- [ ] Implement reports view
- [ ] Add navigation
- [ ] Style all pages

### Frontend - User

- [ ] Create user dashboard
- [ ] Implement form filling interface
- [ ] Create reports view
- [ ] Create user profile page
- [ ] Implement profile editing
- [ ] Add navigation
- [ ] Style all pages

### Integration

- [ ] Connect frontend to backend APIs
- [ ] Implement authentication flow
- [ ] Test form creation and publishing
- [ ] Test form submission
- [ ] Test report generation
- [ ] Test profile updates
- [ ] Verify data sync between admin and user views

### Testing & Deployment

- [ ] Unit testing
- [ ] Integration testing
- [ ] User acceptance testing
- [ ] Performance testing
- [ ] Security audit
- [ ] Deploy to production
- [ ] Monitor and maintain

---

## Key Features Summary

### Admin Capabilities

✅ View analytics dashboard  
✅ Manage clients (CRUD)  
✅ Create custom forms with dynamic fields  
✅ Edit, save, publish, and copy forms  
✅ View client submissions  
✅ Generate and view reports  
✅ Track client progress

### Client Capabilities

✅ View published forms  
✅ Fill and submit forms  
✅ View generated reports  
✅ Edit personal profile  
✅ Track own progress

### Technical Highlights

✅ Role-based authentication (JWT)  
✅ Dynamic form builder (JSONB storage)  
✅ Automated report generation  
✅ Real-time data synchronization  
✅ Responsive design  
✅ RESTful API architecture

---

## Next Steps

1. **Start with Phase 1**: Setup project structure and database
2. **Build Backend First**: Complete all API endpoints
3. **Test APIs**: Use Postman to verify all endpoints
4. **Build Frontend**: Start with shared components, then admin, then user
5. **Integrate**: Connect frontend to backend
6. **Test End-to-End**: Complete user flow testing
7. **Deploy**: Prepare for production deployment

---

## Notes

- Use async/await throughout for better performance
- Implement proper error handling and user feedback
- Keep JSONB structures flexible for future enhancements
- Consider adding WebSocket for real-time updates (future enhancement)
- Plan for scalability (pagination, lazy loading)
- Maintain code documentation and comments
- Follow REST API best practices
- Use semantic HTML and CSS best practices
- Implement progressive enhancement

---

**Project Timeline Estimate:**

- Phase 1-2 (Backend): 3-4 days
- Phase 3 (Frontend): 4-5 days
- Phase 4-5 (Integration & Styling): 2-3 days
- Phase 6-7 (Testing & Deployment): 2-3 days

**Total: 11-15 days** (for a single developer working full-time)
