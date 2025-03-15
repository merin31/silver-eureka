
function parseJwt(token) {
    if (!token) return null;
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(window.atob(base64));
}

function applyRBAC() {
    const user = parseJwt(token);
    const userRole = user?.role;
    
    if (userRole === 'artist') {
        document.querySelector('a[href="/users.html"]').style.display = 'none';
        document.querySelector('a[href="/artists.html"]').style.display = 'none';
    }

    if (userRole === 'artist_manager') {
        document.querySelector('a[href="/users.html"]').style.display = 'none';
    }

    if (userRole !== 'super_admin' && userRole !== 'artist_manager') {
        const addBtn = document.querySelector('.add-btn');
        if (addBtn) addBtn.style.display = 'none';
    }

    if (userRole !== 'super_admin' && userRole !== 'artist_manager') {
        document.querySelectorAll('.edit-btn, .delete-btn').forEach(btn => {
            btn.style.display = 'none';
        });
    }
}