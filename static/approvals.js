// Approvals System (Admin/Teacher)
const approvalsBell = document.getElementById('approvals-bell');
const approvalsModal = document.getElementById('approvals-modal');
const closeApprovals = document.getElementById('close-approvals');
const approvalsList = document.getElementById('approvals-list');
const pendingCountBadge = document.getElementById('pending-count');

// Fetch and update pending count
async function updatePendingCount() {
    if (!approvalsBell) return; // Only for admin/teacher

    try {
        const res = await fetch('/api/pending-events');
        if (res.ok) {
            const pendingEvents = await res.json();
            const count = pendingEvents.length;

            if (count > 0) {
                pendingCountBadge.textContent = count;
                pendingCountBadge.style.display = 'flex';
            } else {
                pendingCountBadge.style.display = 'none';
            }
        }
    } catch (e) {
        console.error('Error fetching pending count:', e);
    }
}

// Show approvals modal (Combined Events and Deletions)
async function showApprovalsModal() {
    try {
        const [pendingRes, delRes] = await Promise.all([
            fetch('/api/pending-events'),
            fetch('/api/deletion-requests')
        ]);

        let pendingEvents = [];
        let deletionRequests = [];

        if (pendingRes.ok) pendingEvents = await pendingRes.json();
        if (delRes.ok) deletionRequests = await delRes.json();

        if (pendingEvents.length === 0 && deletionRequests.length === 0) {
            approvalsList.innerHTML = '<p style="text-align:center; color:var(--text-secondary);">No pending approvals 🎉</p>';
        } else {
            approvalsList.innerHTML = '';

            // 1. Pending Events
            pendingEvents.forEach(event => {
                const card = createApprovalCard(event, 'creation');
                approvalsList.appendChild(card);
            });

            // 2. Deletion Requests
            deletionRequests.forEach(req => {
                const card = createApprovalCard(req, 'deletion');
                approvalsList.appendChild(card);
            });

            // Add Listeners
            bindApprovalListeners();
        }

        approvalsModal.style.display = 'flex';
    } catch (e) {
        console.error('Error loading approvals:', e);
        approvalsList.innerHTML = '<p style="text-align:center; color:#ef4444;">Error loading approvals</p>';
        approvalsModal.style.display = 'flex';
    }
}

function createApprovalCard(item, type) {
    const card = document.createElement('div');
    card.style.cssText = 'background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;';

    let title, meta, badge, approveFn, rejectFn, rejectText;

    if (type === 'creation') {
        title = item.title;
        meta = `<strong>Type:</strong> ${item.type} | <strong>Attendees:</strong> ${item.capacity || 'N/A'}`;
        badge = '<span style="background: rgba(251, 191, 36, 0.15); color: #fbbf24; padding: 0.3rem 0.8rem; border-radius: 8px; font-size: 0.8rem; font-weight: bold;">NEW EVENT</span>';
        approveFn = 'approveEvent';
        rejectFn = 'rejectEvent';
        rejectText = 'Reject';
    } else {
        title = `Deletion: ${item.event_title}`;
        meta = `<strong>Event Type:</strong> ${item.event_type} | <strong>Requested By:</strong> ${item.requested_by_name}`;
        badge = '<span style="background: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 0.3rem 0.8rem; border-radius: 8px; font-size: 0.8rem; font-weight: bold;">DELETION</span>';
        approveFn = 'approveDeletion';
        rejectFn = 'rejectDeletion';
        rejectText = 'Reject Deletion';
    }

    card.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
            <div>
                <h3 style="margin:0 0 0.5rem 0; color:var(--text-primary);">${title}</h3>
                <p style="margin:0; color:var(--text-secondary); font-size:0.9rem;">${meta}</p>
            </div>
            ${badge}
        </div>
        
        <div style="display:flex; gap:0.75rem;">
            <button class="approve-btn" data-id="${item.id}" data-type="${type}" style="flex:1; background: #10b981; color: white; border: none; padding: 0.75rem; border-radius: 8px; cursor: pointer; font-weight: 600;">
                <i class="ph ph-check-circle"></i> Approve
            </button>
            <button class="reject-btn" data-id="${item.id}" data-type="${type}" style="flex:1; background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 0.75rem; border-radius: 8px; cursor: pointer; font-weight: 600;">
                <i class="ph ph-x-circle"></i> ${rejectText}
            </button>
        </div>
    `;
    return card;
}

function bindApprovalListeners() {
    document.querySelectorAll('.approve-btn').forEach(btn => {
        btn.onclick = () => {
            if (btn.dataset.type === 'creation') approveEvent(btn.dataset.id);
            else approveDeletion(btn.dataset.id);
        }
    });

    document.querySelectorAll('.reject-btn').forEach(btn => {
        btn.onclick = () => {
            if (btn.dataset.type === 'creation') rejectEvent(btn.dataset.id);
            else rejectDeletion(btn.dataset.id);
        }
    });
}

// Approve event
async function approveEvent(eventId) {
    if (!confirm('Approve this event?')) return;

    try {
        const res = await fetch(`/api/approve-event/${eventId}`, {
            method: 'POST'
        });

        const data = await res.json();

        if (res.ok && data.success) {
            alert('✅ Event approved successfully!');
            showApprovalsModal(); // Refresh list
            updatePendingCount(); // Update badge
            loadData(); // Refresh dashboard
        } else {
            alert('❌ ' + (data.message || data.error || 'Failed to approve'));
        }
    } catch (e) {
        console.error('Error approving event:', e);
        alert('Error approving event');
    }
}

// Reject event
async function rejectEvent(eventId) {
    const reason = prompt('Reason for rejection (optional):');
    if (reason === null) return; // User cancelled

    try {
        const res = await fetch(`/api/reject-event/${eventId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: reason || 'No reason provided' })
        });

        const data = await res.json();

        if (res.ok && data.success) {
            alert('Event request rejected');
            showApprovalsModal(); // Refresh list
            updatePendingCount(); // Update badge
        } else {
            alert('❌ ' + (data.message || data.error || 'Failed to reject'));
        }
    } catch (e) {
        console.error('Error rejecting event:', e);
        alert('Error rejecting event');
    }
}

async function approveDeletion(reqId) {
    if (!confirm("Confirm deletion of this event?")) return;
    try {
        const res = await fetch(`/api/approve-deletion/${reqId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            alert("Deletion Approved.");
            showApprovalsModal();
            updatePendingCount();
            loadData(); // Update dashboard
        } else {
            alert("Failed: " + (data.error || data.message));
        }
    } catch (e) {
        alert("Error approving deletion.");
    }
}

async function rejectDeletion(reqId) {
    if (!confirm("Reject this deletion request?")) return;
    try {
        const res = await fetch(`/api/reject-deletion/${reqId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            alert("Deletion Rejected.");
            showApprovalsModal();
            updatePendingCount();
        } else {
            alert("Failed: " + (data.error || data.message));
        }
    } catch (e) {
        alert("Error rejecting deletion.");
    }
}

// Event listeners
if (approvalsBell) {
    approvalsBell.addEventListener('click', showApprovalsModal);
    // Update count on page load and every 30 seconds
    updatePendingCount();
    setInterval(updatePendingCount, 30000);
}

if (closeApprovals) {
    closeApprovals.addEventListener('click', () => {
        approvalsModal.style.display = 'none';
    });
}
