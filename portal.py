const saludoTexto = document.getElementById('saludoTexto');
const saludoSubtitulo = document.getElementById('saludoSubtitulo');
const estadoTiempo = document.getElementById('estadoTiempo');
const estadoApps = document.getElementById('estadoApps');
const btnGuardarSalir = document.getElementById('btnGuardarSalir');
const videoIntroContainer = document.getElementById('videoIntroContainer');
const videoIntro = document.getElementById('videoIntro');
const btnIniciarSesion = document.getElementById('btnIniciarSesion');
const estadoSalida = document.getElementById('estadoSalida');
const introSaludo = document.getElementById('introSaludo');

let introOculta = false;
function entrarAlPortal() {
  if (introOculta || !videoIntroContainer) return;
  introOculta = true;
  videoIntroContainer.classList.add('is-hidden');


  setTimeout(() => {
    try { if (videoIntro) videoIntro.pause(); } catch (e) {}
    videoIntroContainer.style.display = 'none';
  }, 950);
}

function prepararIntro() {
  if (!videoIntroContainer || !videoIntro || !btnIniciarSesion) return;

  btnIniciarSesion.addEventListener('click', entrarAlPortal);
  // La intro queda perenne: el video se reproduce en bucle y solo se entra con el boton Iniciar sesion.
  videoIntro.addEventListener('error', () => {
    videoIntroContainer.classList.add('sin-video');
  });

}

function actualizarSaludo() {
  const ahora = new Date();
  const hora = ahora.getHours();
  const minutos = String(ahora.getMinutes()).padStart(2, '0');
  let saludo = 'Buenos días, Francisco Antonio y familia';

  document.body.classList.remove('noche', 'tarde', 'dia');

  if (hora >= 7 && hora < 14) {
    document.body.classList.add('dia');
  } else if (hora >= 14 && hora < 21) {
    saludo = 'Buenas tardes, Francisco Antonio y familia';
    document.body.classList.add('tarde');
  } else {
    saludo = 'Buenas noches, Francisco Antonio y familia';
    document.body.classList.add('noche');
  }

  if (saludoTexto) saludoTexto.textContent = saludo;
  if (saludoSubtitulo) saludoSubtitulo.textContent = 'Selecciona la aplicación que deseas abrir.';
  if (introSaludo) introSaludo.textContent = saludo;
  if (estadoTiempo) {
    estadoTiempo.textContent = `${ahora.toLocaleDateString('es-ES', { weekday: 'long', day: '2-digit', month: 'long' })} · ${hora}:${minutos}`;
  }
}

async function comprobarApps() {
  try {
    const r = await fetch('/estado');
    const data = await r.json();
    const ok1 = data.facturas_presupuestos ? 'Facturas activa' : 'Facturas iniciando';
    const ok2 = data.control_horario ? 'Control horario activo' : 'Control horario iniciando';
    if (estadoApps) estadoApps.textContent = `${ok1} · ${ok2}`;
  } catch (e) {
    if (estadoApps) estadoApps.textContent = 'No se pudo comprobar el estado de las aplicaciones.';
  }
}

async function guardarYSalir() {
  if (!btnGuardarSalir) return;

  const confirmar = window.confirm('Se guardará una copia de seguridad y se cerrarán los módulos abiertos. ¿Quieres continuar?');
  if (!confirmar) return;

  btnGuardarSalir.disabled = true;
  btnGuardarSalir.classList.add('is-saving');
  btnGuardarSalir.textContent = 'Guardando...';
  if (estadoSalida) estadoSalida.textContent = 'Creando copia de seguridad y cerrando servicios con seguridad...';

  try {
    const r = await fetch('/guardar-salir', { method: 'POST' });
    const data = await r.json().catch(() => ({}));

    if (estadoApps) estadoApps.textContent = '';
    if (estadoSalida) {
      estadoSalida.textContent = data.message || 'Datos guardados. Cerrando ventana...';
      estadoSalida.classList.add('ok');
    }

    btnGuardarSalir.textContent = 'Cerrado con seguridad';

    setTimeout(() => {
      document.body.classList.add('modo-cerrado');
      try {
        window.open('', '_self');
        window.close();
      } catch (e) {}
    }, 700);

    setTimeout(() => {
      document.body.innerHTML = `
        <main style="min-height:100vh;display:grid;place-items:center;background:#f7f6f2;font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#102018;text-align:center;padding:30px;">
          <section style="max-width:560px;background:white;border:1px solid #e6e1d8;border-radius:28px;padding:42px;box-shadow:0 24px 70px rgba(0,0,0,.10);">
            <h1 style="margin:0 0 12px;font-size:34px;">Todo guardado</h1>
            <p style="margin:0;color:#66736b;font-size:17px;line-height:1.5;">Los servicios se han cerrado con seguridad. Si esta ventana no se cierra sola, puedes cerrarla manualmente.</p>
          </section>
        </main>`;
    }, 1400);
  } catch (e) {
    btnGuardarSalir.disabled = false;
    btnGuardarSalir.classList.remove('is-saving');
    btnGuardarSalir.textContent = 'Guardar y salir';
    if (estadoSalida) {
      estadoSalida.textContent = 'No se pudo cerrar desde el portal. Revisa la consola del programa.';
      estadoSalida.classList.add('error');
    }
  }
}

if (btnGuardarSalir) {
  btnGuardarSalir.addEventListener('click', guardarYSalir);
}



function optimizarVideoIntro() {
  if (!videoIntro) return;
  videoIntro.setAttribute('preload', 'metadata');
  videoIntro.muted = true;
  videoIntro.playsInline = true;

  document.addEventListener('visibilitychange', () => {
    try {
      if (document.hidden) {
        videoIntro.pause();
      } else if (!introOculta) {
        videoIntro.play().catch(() => {});
      }
    } catch (e) {}
  });
}

optimizarVideoIntro();
prepararIntro();
actualizarSaludo();
comprobarApps();
setInterval(actualizarSaludo, 60000);
setInterval(comprobarApps, 8000);
