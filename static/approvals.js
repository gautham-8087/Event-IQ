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

// Show approvals modal
async function showApprovalsModal() {
    try {
        const res = await fetch('/api/pending-events');
        if (!res.ok) throw new Error('Failed to fetch');

        const pendingEvents = await res.json();

        if (pendingEvents.length === 0) {
            approvalsList.innerHTML = '<p style="text-align:center; color:var(--text-secondary);">No pending approvals 🎉</p>';
        } else {
            approvalsList.innerHTML = '';

            pendingEvents.forEach(event => {
                const card = document.createElement('div');
                card.style.cssText = 'background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 12px; padding: 1.5rem;';

                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                        <div>
                            <h3 style="margin:0 0 0.5rem 0; color:var(--text-primary);">${event.title}</h3>
                            <p style="margin:0; color:var(--text-secondary); font-size:0.9rem;">
                                <strong>Type:</strong> ${event.type} &nbsp;|&nbsp; 
                                <strong>Attendees:</strong> ${event.capacity || 'N/A'}
                            </p>
                        </div>
                        <span style="background: rgba(251, 191, 36, 0.15); color: #fbbf24; padding: 0.3rem 0.8rem; border-radius: 8px; height: fit-content; font-size: 0.8rem; font-weight: bold;">PENDING</span>
                    </div>
                    
                    <div style="margin-bottom:1rem;">
                        <p style="margin:0; color:var(--text-secondary); font-size:0.85rem;">
                            <i class="ph ph-clock"></i> ${new Date(event.start_time).toLocaleString()} - ${new Date(event.end_time).toLocaleTimeString()}
                        </p>
                        <p style="margin:0.5rem 0 0 0; color:var(--text-secondary); font-size:0.85rem;">
                            <i class="ph ph-info"></i> ${event.description || 'No description'}
                        </p>
                    </div>
                    
                    <div style="display:flex; gap:0.75rem;">
                        <button class="approve-btn" data-id="${event.id}" style="flex:1; background: #10b981; color: white; border: none; padding: 0.75rem; border-radius: 8px; cursor: pointer; font-weight: 600;">
                            <i class="ph ph-check-circle"></i> Approve
                        </button>
                        <button class="reject-btn" data-id="${event.id}" style="flex:1; background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); padding: 0.75rem; border-radius: 8px; cursor: pointer; font-weight: 600;">
                            <i class="ph ph-x-circle"></i> Reject
                        </button>
                    </div>
                `;

                approvalsList.appendChild(card);
            });

            // Add event listeners for approve/reject buttons
            document.querySelectorAll('.approve-btn').forEach(btn => {
                btn.addEventListener('click', () => approveEvent(btn.dataset.id));
            });

            document.querySelectorAll('.reject-btn').forEach(btn => {
                btn.addEventListener('click', () => rejectEvent(btn.dataset.id));
            });
        }

        approvalsModal.style.display = 'flex';
    } catch (e) {
        console.error('Error loading approvals:', e);
        approvalsList.innerHTML = '<p style="text-align:center; color:#ef4444;">Error loading approvals</p>';
        approvalsModal.style.display = 'flex';
    }
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
