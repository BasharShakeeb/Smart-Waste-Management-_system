// Collect Me IoT - Main JavaScript

// Global socket connection
let socket;

// Translation helper – reads from window.__T__ (loaded from /api/translations)
function _t(key) {
    return (window.__T__ && window.__T__[key]) || key;
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO connection
    initializeSocket();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });``

    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.main-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    function closeSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('show');
        if (overlay) overlay.classList.remove('active');
    }

    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.add('show');
        if (overlay) overlay.classList.add('active');
    }

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const isMobile = window.innerWidth <= 991;

            if (isMobile) {
                // Mobile/tablet: toggle .show + overlay
                if (sidebar.classList.contains('show')) {
                    closeSidebar();
                } else {
                    openSidebar();
                }
            } else {
                // Desktop: collapse/expand via body class
                document.body.classList.toggle('sidebar-collapsed');
            }
        });
    }

    // Close sidebar when overlay is clicked (mobile)
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 991 && sidebar && sidebar.classList.contains('show')) {
            if (!sidebar.contains(e.target) && sidebarToggle && !sidebarToggle.contains(e.target)) {
                closeSidebar();
            }
        }
    });

    // On window resize, clean up stale states
    window.addEventListener('resize', function() {
        if (window.innerWidth > 991) {
            // Remove mobile .show when switching to desktop
            sidebar && sidebar.classList.remove('show');
            overlay && overlay.classList.remove('active');
        }
    });

    // Initialize charts if present
    initializeCharts();
    
    // Setup page-specific real-time features
    setupPageSpecificRealTime();
});

// Initialize Socket.IO connection
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        showNotification(_t('connectedToServer'), 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        showNotification(_t('disconnectedFromServer'), 'warning');
    });
    
    // Real-time bin updates
    socket.on('bin_status_update', function(data) {
        updateBinStatusInUI(data);
    });
    
    // Dashboard statistics updates
    socket.on('dashboard_stats_update', function(data) {
        updateDashboardStats(data);
    });
    
    // Bin data updates
    socket.on('bin_data_update', function(data) {
        updateBinsTable(data.bins);
    });
    
    // Error handling
    socket.on('error', function(error) {
        console.error('Socket error:', error);
        showNotification(_t('connectionError'), 'error');
    });
}

// Setup page-specific real-time features
function setupPageSpecificRealTime() {
    const currentPath = window.location.pathname;
    
    if (currentPath === '/dashboard' || currentPath === '/') {
        socket.emit('join_dashboard');
        socket.emit('request_dashboard_stats');
        
        // Request updates every 30 seconds
        setInterval(() => {
            socket.emit('request_dashboard_stats');
        }, 30000);
    }
    
    if (currentPath === '/bins') {
        socket.emit('join_bins');
        socket.emit('request_bin_data');
        
        // Request updates every 15 seconds for bins page
        setInterval(() => {
            socket.emit('request_bin_data');
        }, 15000);
    }
    
    if (currentPath === '/drivers') {
        socket.emit('join_drivers');
    }
}

// Update bin status in UI
function updateBinStatusInUI(data) {
    const binElement = document.querySelector(`[data-bin-id="${data.bin_id}"]`);
    if (binElement) {
        // Update fill level
        const fillLevelElement = binElement.querySelector('.fill-level');
        if (fillLevelElement) {
            fillLevelElement.textContent = `${data.fill_level}%`;
            
            // Update progress bar if exists
            const progressBar = binElement.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${data.fill_level}%`;
                progressBar.className = `progress-bar ${getProgressBarClass(data.fill_level)}`;
            }
        }
        
        // Update status badge
        // const statusBadge = binElement.querySelector('.status-badge');
        // if (statusBadge) {
        //     statusBadge.className = `badge ${getStatusBadgeClass(data.status)}`;
        //     statusBadge.textContent = getStatusText(data.status);
        // }
        
        // Add pulse animation for critical bins
        if (data.status === 'critical') {
            binElement.classList.add('critical-bin');
            showNotification(_t('binFullWarning').replace('{binId}', data.bin_id), 'warning');
        } else {
            binElement.classList.remove('critical-bin');
        }
    }
    
    // Update dashboard cards if on dashboard
    if (window.location.pathname === '/dashboard' || window.location.pathname === '/') {
        updateDashboardBinCard(data);
    }
}

// Update dashboard statistics
function updateDashboardStats(data) {
    const elements = {
        'total-bins': data.total_bins,
        'full-bins': data.full_bins,
        'active-bins': data.active_bins,
        'active-drivers': data.active_drivers
    };
    
    Object.keys(elements).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            // Add animation for value change
            element.style.transform = 'scale(1.1)';
            setTimeout(() => {
                element.textContent = elements[key];
                element.style.transform = 'scale(1)';
            }, 150);
        }
    });
    
    // Update timestamp
    const timestampElement = document.getElementById('last-update');
    if (timestampElement) {
        timestampElement.textContent = `${_t('lastUpdate') || 'Last update'}: ${data.timestamp}`;
    }
}

// Update bins table
function updateBinsTable(bins) {
    const tableBody = document.querySelector('#bins-table tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    bins.forEach(bin => {
        const row = createBinTableRow(bin);
        tableBody.appendChild(row);
    });
}

// Create bin table row
function createBinTableRow(bin) {
    const row = document.createElement('tr');
    row.setAttribute('data-bin-id', bin.bin_id);
    
    row.innerHTML = `
        <td>${bin.bin_id}</td>
        <td>${bin.location}</td>
        <td>
            <div class="progress" style="height: 20px;">
                <div class="progress-bar ${getProgressBarClass(bin.fill_level)}" 
                     style="width: ${bin.fill_level}%">
                    ${bin.fill_level}%
                </div>
            </div>
        </td>
        <td>${bin.temperature ? bin.temperature + '°C' : _t('temperatureNA')}</td>
        <td>
            <span class="badge ${getStatusBadgeClass(bin.status)}">
                ${getStatusText(bin.status)}
            </span>
        </td>
        <td>${bin.battery_level}%</td>
        <td>
            <button class="btn btn-sm btn-primary me-1" onclick="showBinDetails('${bin.bin_id}')">
                <i class="fas fa-eye"></i>
            </button>
            <button class="btn btn-sm btn-warning" onclick="createTask(['${bin.bin_id}'])">
                <i class="fas fa-tasks"></i>
            </button>
        </td>
    `;
    
    return row;
}

// Helper functions for status display
function getProgressBarClass(fillLevel) {
    if (fillLevel >= 90) return 'bg-danger';
    if (fillLevel >= 80) return 'bg-warning';
    if (fillLevel >= 50) return 'bg-info';
    return 'bg-success';
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'critical': return 'bg-danger';
        case 'warning': return 'bg-warning';
        case 'normal': return 'bg-success';
        default: return 'bg-secondary';
    }
}

function getStatusText(status) {
    switch (status) {
        case 'critical': return _t('statusCritical');
        case 'warning': return _t('statusWarning');
        case 'normal': return _t('statusNormal');
        default: return _t('notSpecified');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Refresh dashboard data - now using real-time updates
function refreshDashboardData() {
    if (socket && socket.connected) {
        socket.emit('request_dashboard_stats');
        socket.emit('request_bin_data');
    }
}

// Update statistics cards with animation
function updateStatsCards(data) {
    const statsElements = {
        'total-bins': data.total_bins,
        'full-bins': data.full_bins,
        'active-bins': data.active_bins,
        'active-drivers': data.active_drivers
    };

    Object.keys(statsElements).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            // Add pulse animation
            element.classList.add('animate-pulse');
            setTimeout(() => {
                element.textContent = statsElements[key];
                element.classList.remove('animate-pulse');
            }, 200);
        }
    });
}

// Update dashboard bin card with real-time data
function updateDashboardBinCard(binData) {
    const binCard = document.querySelector(`[data-bin-card="${binData.bin_id}"]`);
    if (binCard) {
        const fillLevelElement = binCard.querySelector('.fill-level');
        const progressBar = binCard.querySelector('.progress-bar');
        
        if (fillLevelElement) {
            fillLevelElement.textContent = `${binData.fill_level}%`;
        }
        
        if (progressBar) {
            progressBar.style.width = `${binData.fill_level}%`;
            progressBar.className = `progress-bar ${getProgressBarClass(binData.fill_level)}`;
        }
        
        // Add visual indicator for critical bins
        if (binData.status === 'critical') {
            binCard.classList.add('border-danger', 'shadow-lg');
        } else {
            binCard.classList.remove('border-danger', 'shadow-lg');
        }
    }
}

// Show bin details with real-time data
function showBinDetails(binId) {
    // Request specific bin data
    if (socket) {
        socket.emit('request_bin_details', { bin_id: binId });
    }
    
    // Open modal or navigate to details page
    console.log('Showing details for bin:', binId);
}

// Initialize charts
function initializeCharts() {
    // Collection trend chart
    const collectionTrendCtx = document.getElementById('collectionTrendChart');
    if (collectionTrendCtx) {
        new Chart(collectionTrendCtx, {
            type: 'line',
            data: {
                labels: [_t('dayMon'), _t('dayTue'), _t('dayWed'), _t('dayThu'), _t('dayFri'), _t('daySat'), _t('daySun')],
                datasets: [{
                    label: _t('binsCollected'),
                    data: [12, 19, 3, 5, 2, 3, 8],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Route efficiency chart
    const routeEfficiencyCtx = document.getElementById('routeEfficiencyChart');
    if (routeEfficiencyCtx) {
        new Chart(routeEfficiencyCtx, {
            type: 'bar',
            data: {
                labels: [_t('route1'), _t('route2'), _t('route3'), _t('route4'), _t('route5')],
                datasets: [{
                    label: _t('routeEfficiency'),
                    data: [85, 92, 78, 88, 95],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(39, 174, 96, 0.8)',
                        'rgba(243, 156, 18, 0.8)',
                        'rgba(231, 76, 60, 0.8)',
                        'rgba(155, 89, 182, 0.8)'
                    ],
                    borderColor: [
                        '#3498db',
                        '#27ae60',
                        '#f39c12',
                        '#e74c3c',
                        '#9b59b6'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// Bin management functions
function createTask(binIds) {
    if (!binIds || binIds.length === 0) {
        alert(_t('selectAtLeastOneBin'));
        return;
    }

    // Open task creation modal or redirect to task creation page
    window.location.href = `/create-task?bins=${binIds.join(',')}`;
}

function assignDriver(binId) {
    // Show driver assignment modal
    const modal = new bootstrap.Modal(document.getElementById('assignDriverModal'));
    modal.show();
    
    // Store selected bin ID
    document.getElementById('selectedBinId').value = binId;
}

function updateBinStatus(binId, status) {
    fetch(`/api/bins/${binId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(_t('binStatusUpdateError'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(_t('binStatusUpdateError'));
    });
}

// Driver functions
function startTask(taskId) {
    fetch(`/api/tasks/${taskId}/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(_t('taskStartError'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(_t('taskStartError'));
    });
}

function markBinCollected(taskId, binId) {
    fetch(`/api/tasks/${taskId}/bins/${binId}/collected`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(_t('binCollectError'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(_t('binCollectError'));
    });
}

function completeTask(taskId) {
    if (confirm(_t('confirmCompleteTask'))) {
        fetch(`/api/tasks/${taskId}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
            alert(_t('taskCompleteError'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(_t('taskCompleteError'));
    });
    }
}

// Map functions
function initializeMap() {
    // Initialize map with bins and drivers
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        // This would integrate with a mapping service like Google Maps or Leaflet
        console.log('Initializing map...');
    }
}

function showBinOnMap(binId) {
    // Center map on specific bin
    console.log('Showing bin on map:', binId);
}

function showRouteOnMap(routeId) {
    // Display route on map
    console.log('Showing route on map:', routeId);
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    const loc = window.__LOCALE__ === 'ar' ? 'ar-SA' : 'en-US';
    return date.toLocaleDateString(loc, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    const loc = window.__LOCALE__ === 'ar' ? 'ar-SA' : 'en-US';
    return date.toLocaleTimeString(loc, {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getFillLevelClass(fillLevel) {
    if (fillLevel >= 80) return 'high';
    if (fillLevel >= 40) return 'medium';
    return 'low';
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'full': return 'full';
        case 'half': return 'half';
        case 'empty': return 'empty';
        case 'online': return 'online';
        case 'offline': return 'offline';
        case 'busy': return 'busy';
        default: return 'empty';
    }
}

// Export functions for global access
window.CollectMeIoT = {
    createTask,
    assignDriver,
    updateBinStatus,
    startTask,
    markBinCollected,
    completeTask,
    initializeMap,
    showBinOnMap,
    showRouteOnMap,
    formatDate,
    formatTime,
    getFillLevelClass,
    getStatusBadgeClass
};
