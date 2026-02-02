async function initCamera(){
    const video = document.getElementById('video');
    try {
        const stream = await navigator.mediaDevices.getUserMedia({video: { width: 640, height: 480 }});
        video.srcObject = stream;
    } catch (e) {
        alert('Could not open camera: ' + e);
    }
}
function getCookie(name){
 let cookieValue = null;
 if (document.cookie && document.cookie !== ''){
     const cookies = document.cookie.split(';');
     for (let c of cookies){
         c = c.trim();
         if (c.startsWith(name + '=')){
             cookieValue = c.substring(name.length + 1);
             break;
         }
     }
 }
 return cookieValue;
}
document.getElementById('btnCapture').addEventListener('click', async function(){
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imgData = canvas.toDataURL('image/jpeg');
    const name = document.getElementById('name').value || '';
    const res = await fetch('/capture_face/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({image: imgData, name: name})
    });
    const data = await res.json();
    document.getElementById('msg').innerText = data.message || JSON.stringify(data);
});
window.addEventListener('load', initCamera);
