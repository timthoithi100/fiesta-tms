async function loadAdminDashboard() {
    const container = document.getElementById('admin-dashboard');
    if (!container) return;
    utils.showLoading(container);
    try {
        const data = await utils.apiRequest('/admin/reports/summary');
        document.getElementById('total-students').textContent = data.total_students;
        document.getElementById('active-students').textContent = data.active_students;
        document.getElementById('total-units').textContent = data.total_units;
        document.getElementById('pending-requests').textContent = data.pending_requests;
        document.getElementById('total-collected').textContent = utils.formatCurrency(data.total_fees_collected);
        utils.hideLoading();
    } catch (error) {
        utils.hideLoading();
        utils.showAlert('Failed to load dashboard data: ' + error.message, 'error');
    }
}

async function loadModule(module) {
    const routes = {
        'students': '/admin/students',
        'fee_management': '/admin/fee_management',
        'unit_management': '/admin/unit_management',
        'results_management': '/admin/results_management',
        'clearance_processing': '/admin/clearance_processing',
        'reports': '/admin/reports'
    };
    if (routes[module]) {
        window.location.href = routes[module];
    }
}

async function loadStudents(searchQuery = '') {
    const container = document.getElementById('students-table-body');
    if (!container) return;
    utils.showLoading(container);
    try {
        const url = searchQuery ? `/admin/students?search=${encodeURIComponent(searchQuery)}` : '/admin/students';
        const students = await utils.apiRequest(url);
        if (students.length === 0) {
            container.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No students found</td></tr>';
        } else {
            container.innerHTML = students.map(student => `
                <tr>
                    <td>${student.student_id}</td>
                    <td>${student.first_name} ${student.last_name}</td>
                    <td>${student.program}</td>
                    <td>${student.phone_number}</td>
                    <td>${student.city}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="viewStudent('${student.id}')">View</button></td>
                </tr>
            `).join('');
        }
        utils.hideLoading();
    } catch (error) {
        utils.hideLoading();
        utils.showAlert('Failed to load students: ' + error.message, 'error');
    }
}

function setupStudentSearch() {
    const searchInput = document.getElementById('student-search');
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => { loadStudents(e.target.value); }, 500);
        });
    }
}

async function viewStudent(studentId) {
    try {
        const student = await utils.apiRequest(`/admin/students/${studentId}`);
        alert(`Student: ${student.first_name} ${student.last_name}\nID: ${student.student_id}\nProgram: ${student.program}`);
    } catch (error) {
        utils.showAlert('Failed to load student details: ' + error.message, 'error');
    }
}

async function loadUnits() {
    const container = document.getElementById('units-table-body');
    if (!container) return;
    try {
        const units = await utils.apiRequest('/admin/units');
        container.innerHTML = units.map(unit => `
            <tr>
                <td>${unit.unit_code}</td>
                <td>${unit.unit_name}</td>
                <td>${unit.credits}</td>
                <td><span class="badge bg-${unit.is_active === 'active' ? 'success' : 'secondary'}">${unit.is_active}</span></td>
                <td><button class="btn btn-sm btn-primary" onclick="editUnit('${unit.id}')">Edit</button></td>
            </tr>
        `).join('');
    } catch (error) {
        utils.showAlert('Failed to load units: ' + error.message, 'error');
    }
}

async function createUnit(event) {
    event.preventDefault();
    
    const formData = {
        unit_code: document.getElementById('unit_code').value,
        unit_name: document.getElementById('unit_name').value,
        credits: parseInt(document.getElementById('credits').value),
        description: document.getElementById('description').value || ""
    };

    try {
        // Use the utils.apiRequest if you have it, as it handles the token automatically
        await utils.apiRequest('/admin/units', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        utils.showAlert('Unit created successfully', 'success');
        event.target.reset();
        loadUnits(); 
    } catch (error) {
        // If utils.apiRequest fails, it throws an error we catch here
        utils.showAlert('Failed to create unit: ' + error.message, 'error');
    }
}

async function loadPendingRequests() {
    const container = document.getElementById('requests-table-body');
    if (!container) return;
    try {
        const requests = await utils.apiRequest('/admin/requests?status_filter=pending');
        if (requests.length === 0) {
            container.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No pending requests</td></tr>';
        } else {
            container.innerHTML = requests.map(req => `
                <tr>
                    <td>${req.student.student_id}</td>
                    <td>${req.student.first_name} ${req.student.last_name}</td>
                    <td><span class="badge bg-info">${req.request_type}</span></td>
                    <td>${utils.formatDate(req.request_date)}</td>
                    <td>${req.student_remarks || '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="processRequest('${req.id}', 'approved')">Approve</button>
                        <button class="btn btn-sm btn-danger" onclick="processRequest('${req.id}', 'rejected')">Reject</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        utils.showAlert('Failed to load requests: ' + error.message, 'error');
    }
}

async function processRequest(requestId, status) {
    const remarks = prompt(`Enter ${status} remarks (optional):`);
    try {
        await utils.apiRequest(`/admin/requests/${requestId}`, {
            method: 'PUT',
            body: JSON.stringify({ status: status, admin_remarks: remarks })
        });
        utils.showAlert(`Request ${status} successfully`, 'success');
        loadPendingRequests();
    } catch (error) {
        utils.showAlert('Failed to process request: ' + error.message, 'error');
    }
}

async function recordPayment(event) {
    event.preventDefault();
    const formData = {
        student_id: document.getElementById('student_id').value,
        amount: parseFloat(document.getElementById('amount').value),
        payment_method: document.getElementById('payment_method').value,
        reference_number: document.getElementById('reference_number').value,
        academic_year: document.getElementById('academic_year').value,
        semester: document.getElementById('semester').value,
        remarks: document.getElementById('remarks').value || null
    };
    try {
        await utils.apiRequest('/admin/payments', { method: 'POST', body: JSON.stringify(formData) });
        utils.showAlert('Payment recorded successfully', 'success');
        event.target.reset();
    } catch (error) {
        utils.showAlert('Failed to record payment: ' + error.message, 'error');
    }
}

window.loadModule = loadModule;

document.addEventListener('DOMContentLoaded', () => {
    if (!utils.protectRoute('admin')) return;
    const path = window.location.pathname;
    if (path.includes('/admin/home')) {
        loadAdminDashboard();
    } else if (path.includes('students')) {
        loadStudents();
        setupStudentSearch();
    } else if (path.includes('unit_management')) {
        loadUnits();
        document.getElementById('create-unit-form')?.addEventListener('submit', createUnit);
    } else if (path.includes('clearance_processing')) {
        loadPendingRequests();
    } else if (path.includes('fee_management')) {
        document.getElementById('payment-form')?.addEventListener('submit', recordPayment);
    }
});