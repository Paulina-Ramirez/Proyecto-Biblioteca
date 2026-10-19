const API = location.port === "8000" ? "" : "http://127.0.0.1:8000";
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt = d => d ? new Date(d).toLocaleDateString("es-MX") : "—";
const getMe = () => { try { return JSON.parse(localStorage.getItem("me") || "null"); } catch { return null; } };
const librarian = () => getMe()?.rol === "Bibliotecario";

async function api(path, options={}) {
  let response;
  try { response = await fetch(API + path, {...options, headers:{"Content-Type":"application/json"}, body:options.body ? JSON.stringify(options.body) : undefined}); }
  catch { throw Error("No hay conexión con la API. Comprueba que Uvicorn esté ejecutándose."); }
  if (response.status === 204) return null;
  const data = await response.json().catch(()=>null);
  if (!response.ok) { const d=data?.detail; throw Error(typeof d==="string" ? d : Array.isArray(d) ? d.map(x=>x.msg).join(". ") : "Error del servidor ("+response.status+")"); }
  return data;
}

function toast(message, error=false) {
  const node=document.createElement("div");
  node.textContent=message;
  if(error) node.classList.add("e");
  document.querySelector("#toast")?.append(node);
  if(!document.querySelector("#toast")) {
    node.style.cssText=`position:fixed;right:20px;bottom:20px;padding:13px 18px;border-radius:10px;background:${error?"#9D3445":"#42613D"};color:white;z-index:99`;
    document.body.append(node);
  }
  setTimeout(()=>node.remove(),5000);
}

function guard() { if(!getMe()) location.href="index.html"; }

function iconSvg(name) {
 const paths = {
  home:'<path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/>',
  books:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/><path d="M8 7h8M8 11h7"/>',
  users:'<path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  loans:'<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/>',
  alert:'<path d="m10.3 3.9-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3.1l-8-14a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
  returns:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/><path d="M9 14l-2-2 2-2"/><path d="M7 12h6"/>'
 };
 return `<span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${paths[name]||paths.books}</svg></span>`;
}

function layout(active) {
 const me=getMe();
 const links = [
    ["dashboard.html","Inicio","home"],
    ["libros.html",librarian()?"Libros":"Catálogo","books"],
    ...(librarian()?[["usuarios.html","Usuarios","users"]]:[]),
    ["prestamos.html",librarian()?"Préstamos":"Mis préstamos","loans"],
    ...(librarian()?[["devoluciones.html","Devoluciones","returns"]]:[]),
    ["sanciones.html",librarian()?"Sanciones":"Mis sanciones","alert"]
 ];
 
 document.querySelector("#app-shell").innerHTML=`
 <div class="page-shell">
   <nav class="sidebar">
     <div class="brand">Cozy Biblioteca<small>Un espacio para leer</small></div>
     ${links.map(([href,label,icon])=>`<a class="${href===active?"active":""}" href="${href}">${iconSvg(icon)}<span>${label}</span></a>`).join("")}
   </nav>
   <div class="content">
     <div class="top">
       <span class="brand">Cozy Biblioteca</span>
       <div class="u">
         <div class="av">${esc((me?.nombre||"?").split(" ").map(x=>x[0]).slice(0,2).join("").toUpperCase())}</div>
         <div>
           <a href="perfil.html" style="color: inherit; text-decoration: none; border-bottom: 1px dashed var(--muted);">
             <b>${esc(me?.nombre)}</b>
           </a>
           <br><small class="mu">${esc(me?.rol)}</small>
         </div>
         <button class="sm" id="logout">Salir</button>
       </div>
     </div>
     <main class="pg" id="page"></main>
   </div>
 </div>`;
 
 $("#logout").onclick=()=>{localStorage.removeItem("me");location.href="index.html";};
}