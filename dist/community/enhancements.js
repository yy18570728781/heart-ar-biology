/* Runs after app.js parsing: upgrades the built-in catalogue player. */
setTimeout(() => {
  preview = async function () {
    const r = current;
    if (!r || !r.available) { toast('该课程内容暂未接入。'); return; }
    trials[r.id] = (trials[r.id] || 0) + 1;
    localStorage.setItem('community-trials', JSON.stringify(trials));
    open(`<div class="viewerbar"><b>▣ ${esc(r.title)}</b><span>试用中 · 鼠标、触屏和键盘都可操作</span><button data-download>↓ 下载离线课件</button><button data-close>× 关闭</button></div><iframe title="课件预览" sandbox="allow-scripts" referrerpolicy="no-referrer"></iframe>`, 'viewer');
    const frame = modal.querySelector('iframe');
    if (r.builtin) frame.srcdoc = Lessons.html(r.id);
    else if (r.file && /\.html?$/i.test(r.file.name)) frame.srcdoc = await r.file.text();
    else if (r.link) frame.src = r.link;
    else frame.srcdoc = '<h2>该资源暂不支持在线预览</h2>';
  };
  download = function () {
    const r = current;
    if (!r || !r.available) { toast('该课程文件尚未接入。'); return; }
    const blob = r.file || (r.builtin ? new Blob([Lessons.html(r.id)], {type:'text/html'}) : null);
    if (!blob) { toast('该课件暂不支持单文件下载。'); return; }
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = r.file?.name || `${r.title}.html`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
    toast('已开始下载离线课件');
  };
}, 0);
