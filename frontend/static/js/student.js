async function loadDashboard() {
    const container = document.getElementById('dashboard-data');
    if (!container) return;
    utils.showLoading(container);
    try {
        const data = await utils.apiRequest('/student/dashboard');
        updateDashboardTiles(data);
        utils.hideLoading();
    } catch (error) {
        utils.hideLoading();
        utils.showAlert('Failed to load dashboard data: ' + error.message, 'error');
    }
}

function updateDashboardTiles(data) {
    const registeredUnits = document.getElementById('registered-units');
    if (registeredUnits) registeredUnits.textContent = data.registered_units_count;
    const attemptedUnits = document.getElementById('attempted-units');
    if (attemptedUnits) attemptedUnits.textContent = data.attempted_units_count;
    const feeBalance = document.getElementById('fee-balance');
    if (feeBalance) {
        feeBalance.textContent = utils.formatCurrency(data.fee_balance);
        feeBalance.style.color = data.fee_balance > 0 ? '#e74c3c' : '#27ae60';
    }
    const studentInfo = data.student_info;
    const studentName = document.getElementById('student-name');
    if (studentName) studentName.textContent = `${studentInfo.first_name} ${studentInfo.last_name}`;
}

async function loadPersonalInfo() {
    const container = document.getElementById('personal-info-form');
    if (!container) return;
    try {
        const data = await utils.apiRequest('/student/profile');
        container.innerHTML = `
            <form id="profile-update-form" class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">First Name</label>
                    <input type="text" id="first_name" class="form-control" value="${data.first_name}" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Last Name</label>
                    <input type="text" id="last_name" class="form-control" value="${data.last_name}" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Phone Number</label>
                    <input type="text" id="phone_number" class="form-control" value="${data.phone_number}" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">City</label>
                    <input type="text" id="city" class="form-control" value="${data.city}" required>
                </div>
                <div class="col-12 text-end">
                    <button type="submit" class="btn btn-primary">Update Profile</button>
                </div>
            </form>`;
        document.getElementById('profile-update-form').addEventListener('submit', updatePersonalInfo);
    } catch (error) {
        utils.showAlert('Failed to load profile: ' + error.message, 'error');
    }
}

async function updatePersonalInfo(event) {
    event.preventDefault();
    const formData = {
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        phone_number: document.getElementById('phone_number').value,
        city: document.getElementById('city').value
    };
    try {
        await utils.apiRequest('/student/profile', {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
        utils.showAlert('Profile updated successfully', 'success');
    } catch (error) {
        utils.showAlert('Update failed: ' + error.message, 'error');
    }
}

async function loadFeesStatement() {
    const container = document.getElementById('fees-table');
    if (!container) return;
    try {
        const data = await utils.apiRequest('/student/fees/statement');
        container.innerHTML = `
            <div class="alert ${data.balance > 0 ? 'alert-danger' : 'alert-success'}">
                <strong>Current Balance: ${utils.formatCurrency(data.balance)}</strong>
            </div>
            <table class="table mt-3">
                <thead>
                    <tr><th>Date</th><th>Description</th><th>Ref</th><th>Amount</th></tr>
                </thead>
                <tbody>
                    ${data.transactions.map(t => `
                        <tr>
                            <td>${utils.formatDate(t.date)}</td>
                            <td>${t.description}</td>
                            <td>${t.reference_number || '-'}</td>
                            <td>${utils.formatCurrency(t.amount)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>`;
    } catch (error) {
        utils.showAlert('Failed to load fees', 'error');
    }
}

async function loadUnitRegistration() {
    const container = document.getElementById('unit-registration-table');
    if (!container) return;
    try {
        const units = await utils.apiRequest('/student/units/available');
        container.innerHTML = `
            <table class="table">
                <thead><tr><th>Code</th><th>Name</th><th>Credits</th><th>Action</th></tr></thead>
                <tbody>
                    ${units.map(u => `
                        <tr>
                            <td>${u.unit_code}</td>
                            <td>${u.unit_name}</td>
                            <td>${u.credits}</td>
                            <td><button class="btn btn-sm btn-success" onclick="registerUnit('${u.id}')">Register</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>`;
    } catch (error) {
        utils.showAlert('Failed to load units', 'error');
    }
}

async function registerUnit(unitId) {
    try {
        await utils.apiRequest('/student/units/register', {
            method: 'POST',
            body: JSON.stringify({ unit_id: unitId })
        });
        utils.showAlert('Registered!', 'success');
        loadUnitRegistration();
    } catch (error) {
        utils.showAlert(error.message, 'error');
    }
}

async function loadResults() {
    const container = document.getElementById('results-table-body');
    if (!container) return;
    try {
        const results = await utils.apiRequest('/student/results');
        container.innerHTML = results.map(r => `
            <tr>
                <td>${r.unit_code}</td>
                <td>${r.unit_name}</td>
                <td>${r.grade}</td>
                <td>${r.marks}</td>
            </tr>
        `).join('');
    } catch (error) {
        container.innerHTML = '<tr><td colspan="4">No results found</td></tr>';
    }
}

async function loadRequests() {
    const container = document.getElementById('requests-list');
    if (!container) return;
    try {
        const requests = await utils.apiRequest('/student/requests');
        container.innerHTML = requests.map(req => `
            <div class="card mb-2">
                <div class="card-body">
                    <h6>${req.request_type.toUpperCase()}</h6>
                    <span class="badge bg-secondary">${req.status}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = 'No requests found.';
    }
}

// Add this function to student.js
async function submitRequest(requestType) {
    const remarks = document.getElementById(`${requestType}-remarks`).value;
    
    try {
        await utils.apiRequest('/student/requests', {
            method: 'POST',
            body: JSON.stringify({
                request_type: requestType,
                student_remarks: remarks
            })
        });
        
        utils.showAlert(`${requestType.charAt(0).toUpperCase() + requestType.slice(1)} request submitted successfully`, 'success');
        document.getElementById(`${requestType}-remarks`).value = '';
        loadRequests();
    } catch (error) {
        utils.showAlert('Failed to submit request: ' + error.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!utils.protectRoute('student')) return;
    const path = window.location.pathname;
    if (path.includes('/student/home')) loadDashboard();
    if (path.includes('personal_info')) loadPersonalInfo();
    if (path.includes('fees')) loadFeesStatement();
    if (path.includes('unit_registration')) loadUnitRegistration();
    if (path.includes('results')) loadResults();
    if (path.includes('graduation') || path.includes('clearance')) loadRequests();
});

window.submitRequest = submitRequest;
window.registerUnit = registerUnit;