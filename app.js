/* JATH Electroestatic - catalogo vivo
   Corre sin internet y sin servidor: todo esta en archivos sueltos al lado. Por eso nada de
   fetch ni de modulos, y el boton de WhatsApp es un enlace normal. */
(function () {
  'use strict';

  var D = window.DATOS;
  // La clave cambio de nombre cuando la marca se corrigio. Si se dejara la misma, un cliente
  // que todavia tenga la cotizacion guardada de la version anterior veria sus items viejos
  // mezclados con los nuevos, sin saber de donde salieron.
  var CLAVE = 'jath-electroestatic-cotizacion-v1';
  var WA = 'https://wa.me/' + D.contacto.whatsapp_numero;

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  var colorPorId = {}, equipoPorId = {};
  D.colores.forEach(function (c) { colorPorId[c.id] = c; });
  D.equipos.forEach(function (e) { equipoPorId[e.id] = e; });

  var dispararChorroPistola = null;

  // ---------------------------------------------------------------- escena del encabezado
  // La pistola dispara un abanico de pintura: cada gota es un div vacio que cruza la cinta de
  // 0% a 100% abriendose en cono. Se hacen con codigo y no como HTML escrito a mano porque los
  // parametros son aleatorios: asi la nube no se ve como una hilera de puntos identicos. Los
  // retrasos van en negativo para que el chorro ya este en marcha al cargar la pagina.
  (function escena() {
    var caja = $('#escena-polvo');
    if (!caja) return;
    // Las gotas se crean siempre: el chorro es el efecto principal de la portada y debe
    // animarse aunque el telefono tenga activado "reducir movimiento".
    // La abertura se mide en pantalla en vez de escribirse a mano: asi la nube copia el
    // abanico dibujado en CSS, y no se sale de la cinta en celular ni queda raquitica en
    // pantalla ancha.
    var cono = document.querySelector('.escena-abanico');
    var medio = (cono ? cono.getBoundingClientRect().height : 156) / 2;
    var N = 72;
    // Paleta de varios colores vivos de pintura electrostática
    var paleta = [
      { hex: '#0573BC', rgb: '5, 115, 188' },   // Azul Caribe
      { hex: '#469D39', rgb: '70, 157, 57' },   // Verde Menta
      { hex: '#EAAA0D', rgb: '234, 170, 13' },  // Amarillo Liso
      { hex: '#E25327', rgb: '226, 83, 39' },   // Naranja Liso
      { hex: '#C1121F', rgb: '193, 18, 31' },   // Rojo Liso
      { hex: '#D0326D', rgb: '208, 50, 109' },  // Fucsia Magenta
      { hex: '#7C649D', rgb: '124, 100, 157' }, // Lila
      { hex: '#00A896', rgb: '0, 168, 150' },   // Turquesa
      { hex: '#C99E32', rgb: '201, 158, 50' },  // Dorado
      { hex: '#0D3884', rgb: '13, 56, 132' }    // Azul Cobalto
    ];
    for (var i = 0; i < N; i++) {
      var p = document.createElement('i');
      // --x0 escalona la salida para que la boquilla escupa ancho desde el primer instante y
      // --dy es la altura a la que llega la gota al final, repartida dentro del abanico.
      var x0 = Math.random() * 20;
      var dy = (Math.random() * 2 - 1) * medio * 0.9;
      var dur = 1.4 + Math.random() * 1.3;
      var col = paleta[i % paleta.length];
      p.style.setProperty('--x0', x0.toFixed(1) + 'px');
      p.style.setProperty('--dy', dy.toFixed(1) + 'px');
      p.style.setProperty('--dur', dur.toFixed(2) + 's');
      p.style.setProperty('--tam', (0.45 + Math.random() * 0.8).toFixed(2));
      p.style.setProperty('--ret', (-Math.random() * dur).toFixed(2) + 's');
      p.style.setProperty('--color-gota', col.hex);
      p.style.setProperty('--sombra-gota', 'rgba(' + col.rgb + ', 0.65)');
      caja.appendChild(p);
    }

    // El ancho del abanico se mide y se guarda en --recorrido: la animacion mueve las gotas
    // con transform (no con left), y asi el navegador no recalcula la pagina en cada cuadro.
    // Si cambia el tamano de la ventana se vuelve a medir.
    function medirRecorrido() {
      caja.style.setProperty('--recorrido', caja.clientWidth + 'px');
    }
    medirRecorrido();
    var espera = null;
    window.addEventListener('resize', function () {
      if (espera) return;
      espera = window.setTimeout(function () { espera = null; medirRecorrido(); }, 200);
    });

    // Fuera de pantalla no se anima nada: la cinta queda congelada mientras se lee el resto.
    var cinta = document.querySelector('.escena');
    if (cinta && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (entradas) {
        cinta.classList.toggle('escena-quieta', !entradas[0].isIntersecting);
      }, { rootMargin: '120px' }).observe(cinta);
    }

    // Disparador de ráfagas personalizadas desde la pistola
    dispararChorroPistola = function (colorObj, cantidad) {
      if (!caja) return;
      var total = cantidad || 26;
      for (var k = 0; k < total; k++) {
        (function () {
          var p = document.createElement('i');
          var dy = (Math.random() * 2 - 1) * medio * 0.95;
          var dur = 0.9 + Math.random() * 0.8;
          var c = colorObj || paleta[Math.floor(Math.random() * paleta.length)];
          p.style.setProperty('--x0', (Math.random() * 15).toFixed(1) + 'px');
          p.style.setProperty('--dy', dy.toFixed(1) + 'px');
          p.style.setProperty('--dur', dur.toFixed(2) + 's');
          p.style.setProperty('--tam', (0.65 + Math.random() * 0.85).toFixed(2));
          p.style.setProperty('--ret', '0s');
          p.style.setProperty('--color-gota', c.hex);
          p.style.setProperty('--sombra-gota', c.sombra || ('rgba(' + (c.rgb || '193,18,31') + ', 0.85)'));
          caja.appendChild(p);
          window.setTimeout(function () {
            if (p.parentNode) p.parentNode.removeChild(p);
          }, (dur + 0.1) * 1000);
        }());
      }
    };

    // Al hacer clic en la pistola o en la escena, dispara una ráfaga multicolor
    var escenaEl = document.querySelector('.escena');
    if (escenaEl) {
      escenaEl.style.cursor = 'pointer';
      escenaEl.title = 'Haga clic para disparar una ráfaga multicolor';
      escenaEl.addEventListener('click', function () {
        dispararChorroPistola(null, 24);
      });
    }
  }());

  // ---------------------------------------------------------------- memoria
  // En file:// el navegador a veces no deja guardar, y no es motivo para que el sitio
  // deje de funcionar: se intenta y, si falla, sigue igual mientras esta abierto.
  function cargar() {
    try {
      var s = window.localStorage.getItem(CLAVE);
      return s ? JSON.parse(s) : [];
    } catch (e) { return []; }
  }
  function guardar(items) {
    try { window.localStorage.setItem(CLAVE, JSON.stringify(items)); } catch (e) {}
  }

  var carrito = cargar();

  function sumar(tipo, id) {
    for (var i = 0; i < carrito.length; i++) {
      if (carrito[i].tipo === tipo && carrito[i].id === id) {
        carrito[i].cantidad += 1;
        return;
      }
    }
    carrito.push({ tipo: tipo, id: id, cantidad: 1 });
  }
  function restar(tipo, id) {
    for (var i = 0; i < carrito.length; i++) {
      if (carrito[i].tipo === tipo && carrito[i].id === id) {
        carrito[i].cantidad -= 1;
        if (carrito[i].cantidad <= 0) carrito.splice(i, 1);
        return;
      }
    }
  }
  function quitar(tipo, id) {
    carrito = carrito.filter(function (i) { return !(i.tipo === tipo && i.id === id); });
  }
  function total() {
    return carrito.reduce(function (s, i) { return s + i.cantidad; }, 0);
  }

  // ---------------------------------------------------------------- avisos
  var reloj = null;
  function avisar(texto) {
    var caja = $('#avisos');
    // Un aviso a la vez. Antes se apilaban: cada temporizador quitaba solo el suyo, asi que
    // agregar cinco cosas seguidas dejaba cinco avisos pegados en la pantalla.
    caja.innerHTML = '';
    var n = document.createElement('div');
    n.className = 'aviso-flotante';
    n.textContent = texto;
    caja.appendChild(n);
    if (reloj) window.clearTimeout(reloj);
    reloj = window.setTimeout(function () {
      if (n.parentNode) n.parentNode.removeChild(n);
    }, 2400);
  }

  // ---------------------------------------------------------------- textos del folleto
  $('#mision').textContent = D.mision;
  $('#vision').textContent = D.vision;
  $('#portada-bajada').textContent = D.quienes_somos;
  $('#lema').textContent = D.contacto.lema;

  // Las cifras de la portada cuentan solas al abrir, menos para quien pidio menos movimiento.
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function contarCifra(nodo, numero, cola) {
    if (quieto || numero < 2) { nodo.textContent = numero + cola; return; }
    var t0 = null;
    function paso(t) {
      if (t0 === null) t0 = t;
      var k = Math.min(1, (t - t0) / 900);
      nodo.textContent = Math.round(numero * (1 - Math.pow(1 - k, 3))) + cola;
      if (k < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }
  var cifras = $('#cifras');
  cifras.innerHTML = '';
  var itemsCifras = [
    {
      cifra: '48',
      titulo: 'colores en la carta',
      accion: 'Ver carta',
      destino: 'colores',
      color: { hex: '#0573BC', rgb: '5, 115, 188', sombra: 'rgba(5, 115, 188, 0.28)' }
    },
    {
      cifra: '15',
      titulo: 'equipos y repuestos',
      accion: 'Ver equipos',
      destino: 'equipos',
      color: { hex: '#2D8A4E', rgb: '45, 138, 78', sombra: 'rgba(45, 138, 78, 0.28)' }
    },
    {
      cifra: '4',
      titulo: 'líneas de servicio',
      accion: 'Ver servicios',
      destino: 'servicios',
      color: { hex: '#D96B27', rgb: '217, 107, 39', sombra: 'rgba(217, 107, 39, 0.28)' }
    },
    {
      cifra: '10+',
      titulo: 'años de experiencia',
      accion: 'Conózcanos',
      destino: 'quienes',
      color: { hex: '#C1121F', rgb: '193, 18, 31', sombra: 'rgba(193, 18, 31, 0.28)' }
    }
  ];

  itemsCifras.forEach(function (c) {
    var li = document.createElement('li');
    li.setAttribute('role', 'button');
    li.setAttribute('tabindex', '0');
    li.setAttribute('title', 'Haga clic para ver ' + c.titulo);
    li.style.setProperty('--cifra-color', c.color.hex);
    li.style.setProperty('--cifra-sombra', c.color.sombra);

    var b = document.createElement('b');
    var s = document.createElement('span');
    var acc = document.createElement('small');
    acc.className = 'cifra-accion';
    acc.innerHTML = c.accion + ' <i aria-hidden="true">&rarr;</i>';

    var partes = /^(\d+)(.*)$/.exec(c.cifra);
    b.textContent = c.cifra;
    s.textContent = c.titulo;
    li.appendChild(b);
    li.appendChild(s);
    li.appendChild(acc);
    cifras.appendChild(li);

    contarCifra(b, parseInt(partes[1], 10), partes[2]);

    function activarCifra() {
      if (dispararChorroPistola) {
        dispararChorroPistola(c.color, 32);
      }
      contarCifra(b, parseInt(partes[1], 10), partes[2]);
      li.classList.add('cifra-activa');
      window.setTimeout(function () {
        li.classList.remove('cifra-activa');
      }, 350);

      var destinoEl = document.getElementById(c.destino);
      if (destinoEl) {
        destinoEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    li.addEventListener('click', activarCifra);
    li.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activarCifra();
      }
    });
  });

  // Modal de cobertura y zonas de despacho
  function abrirModalCobertura() {
    var modal = $('#modal-cobertura');
    if (!modal) return;
    var btnWa = $('#btn-cobertura-wa');
    if (btnWa) {
      var msg = encodeURIComponent('Hola JATH Electroestatic, me gustaría consultar tiempos de entrega y flete para mi ciudad.');
      btnWa.href = 'https://wa.me/' + D.contacto.whatsapp_numero + '?text=' + msg;
    }
    modal.hidden = false;
  }
  function cerrarModalCobertura() {
    var modal = $('#modal-cobertura');
    if (modal) modal.hidden = true;
  }
  $$('[data-cerrar-cobertura]').forEach(function (btn) {
    btn.addEventListener('click', cerrarModalCobertura);
  });

  var dif = $('#diferenciadores');
  var datosDif = [
    {
      tipo: 'experiencia',
      titulo: (D.diferenciadores[0] && D.diferenciadores[0][0]) || 'Más de 10 años de experiencia',
      desc: (D.diferenciadores[0] && D.diferenciadores[0][1]) || 'Trayectoria y solidez garantizada en el mercado.',
      pista: 'Ver fotos de trabajos',
      icono: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>',
      color: { hex: '#C1121F', rgb: '193, 18, 31' },
      aviso: 'Conozca nuestros trabajos y aplicaciones en pintura electrostática.'
    },
    {
      tipo: 'asesor',
      titulo: (D.diferenciadores[1] && D.diferenciadores[1][0]) || 'Asesoría personalizada',
      desc: (D.diferenciadores[1] && D.diferenciadores[1][1]) || 'Un asesor técnico que conoce su caso.',
      pista: 'Contactar por WhatsApp',
      icono: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
      color: { hex: '#0573BC', rgb: '5, 115, 188' },
      aviso: 'Conectando con un asesor técnico por WhatsApp...'
    },
    {
      tipo: 'productos',
      titulo: (D.diferenciadores[2] && D.diferenciadores[2][0]) || 'Productos de alto rendimiento',
      desc: (D.diferenciadores[2] && D.diferenciadores[2][1]) || 'Pinturas y equipos de calidad superior.',
      pista: 'Ver catálogo de productos',
      icono: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
      color: { hex: '#D96B27', rgb: '217, 107, 39' },
      aviso: 'Explorando la línea de pinturas y equipos de aplicación.'
    },
    {
      tipo: 'entrega',
      titulo: (D.diferenciadores[3] && D.diferenciadores[3][0]) || 'Entrega ágil en Bogotá y alrededores',
      desc: (D.diferenciadores[3] && D.diferenciadores[3][1]) || 'Mismo día en Bogotá y cobertura a nivel nacional.',
      pista: 'Ver mapa de cobertura',
      icono: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13" rx="1"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
      color: { hex: '#2D8A4E', rgb: '45, 138, 78' },
      aviso: 'Abriendo mapa de cobertura y zonas de despacho...'
    }
  ];

  dif.innerHTML = '';
  datosDif.forEach(function (d, idx) {
    var li = document.createElement('li');
    li.setAttribute('role', 'button');
    li.setAttribute('tabindex', '0');
    li.setAttribute('aria-label', d.titulo + ': ' + d.desc + '. ' + d.pista);
    li.style.setProperty('--dif-color', d.color.hex);
    li.style.setProperty('--dif-sombra', 'rgba(' + d.color.rgb + ', 0.22)');
    li.style.setProperty('--dif-fondo', 'rgba(' + d.color.rgb + ', 0.08)');

    var cab = document.createElement('div');
    cab.className = 'dif-cabecera';
    cab.innerHTML = '<div class="dif-icono" aria-hidden="true">' + d.icono + '</div><span class="dif-numero">0' + (idx + 1) + '</span>';

    var tit = document.createElement('strong');
    tit.className = 'dif-titulo';
    tit.textContent = d.titulo;

    var desc = document.createElement('span');
    desc.className = 'dif-desc';
    desc.textContent = d.desc;

    var pis = document.createElement('small');
    pis.className = 'dif-pista';
    pis.innerHTML = d.pista + ' <i aria-hidden="true">&rarr;</i>';

    li.appendChild(cab);
    li.appendChild(tit);
    li.appendChild(desc);
    li.appendChild(pis);
    dif.appendChild(li);

    function activarDif() {
      if (dispararChorroPistola) {
        dispararChorroPistola(d.color, 28);
      }
      li.classList.add('diferenciador-activo');
      window.setTimeout(function () {
        li.classList.remove('diferenciador-activo');
      }, 300);
      avisar(d.aviso);

      // Acciones solicitadas para cada tarjeta
      if (d.tipo === 'experiencia') {
        var secTrabajos = document.getElementById('trabajos');
        if (secTrabajos) secTrabajos.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else if (d.tipo === 'asesor') {
        var msg = encodeURIComponent('Hola JATH Electroestatic, me contacto desde la web y solicito asesoría personalizada para un proyecto.');
        window.open('https://wa.me/' + D.contacto.whatsapp_numero + '?text=' + msg, '_blank', 'noopener');
      } else if (d.tipo === 'productos') {
        var secProductos = document.getElementById('productos');
        if (secProductos) secProductos.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else if (d.tipo === 'entrega') {
        abrirModalCobertura();
      }
    }

    li.addEventListener('click', activarDif);
    li.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activarDif();
      }
    });
  });

  // Renderizar galería de trabajos
  var galeriaTrabajos = $('#galeria-trabajos');
  if (galeriaTrabajos) {
    var listaTrabajos = [
      {
        titulo: 'Estructuras y Rejas Metálicas',
        categoria: 'Arquitectónico & Seguridad',
        foto: 'fotos/trabajo-01.jpg'
      },
      {
        titulo: 'Perfiles de Aluminio',
        categoria: 'Ventanería & Fachadas',
        foto: 'fotos/trabajo-02.jpg'
      },
      {
        titulo: 'Autopartes y Rines de Aleación',
        categoria: 'Sector Automotriz',
        foto: 'fotos/trabajo-03.jpg'
      },
      {
        titulo: 'Gabinetes Eléctricos y Racks',
        categoria: 'Equipos Electrónicos',
        foto: 'fotos/trabajo-04.jpg'
      },
      {
        titulo: 'Mobiliario Comercial y Estantería',
        categoria: 'Diseño & Retail',
        foto: 'fotos/trabajo-05.jpg'
      },
      {
        titulo: 'Maquinaria y Tuberías Pesadas',
        categoria: 'Sector Industrial',
        foto: 'fotos/trabajo-06.jpg'
      }
    ];

    galeriaTrabajos.innerHTML = '';
    listaTrabajos.forEach(function (tr) {
      var art = document.createElement('article');
      art.className = 'tarjeta-trabajo';

      var wrap = document.createElement('div');
      wrap.className = 'trabajo-foto-wrap';
      wrap.innerHTML = '<img src="' + tr.foto + '" alt="' + tr.titulo + '" loading="lazy" decoding="async"><span class="trabajo-badge">Muestra referencial</span>';

      var info = document.createElement('div');
      info.className = 'trabajo-info';
      info.innerHTML = '<span class="trabajo-categoria">' + tr.categoria + '</span>' +
        '<h3 class="trabajo-titulo">' + tr.titulo + '</h3>';

      art.appendChild(wrap);
      art.appendChild(info);
      galeriaTrabajos.appendChild(art);
    });
  }

  // Interactividad en tarjetas de Misión y Visión
  var tMision = $('.tarjeta-mision');
  if (tMision) {
    tMision.style.cursor = 'pointer';
    tMision.addEventListener('click', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: '#0573BC', rgb: '5, 115, 188' }, 26);
      avisar('Misión JATH: eficiencia y resultados superiores en recubrimiento industrial.');
    });
  }
  var tVision = $('.tarjeta-vision');
  if (tVision) {
    tVision.style.cursor = 'pointer';
    tVision.addEventListener('click', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: '#2D8A4E', rgb: '45, 138, 78' }, 26);
      avisar('Visión JATH: liderazgo en tecnologías limpias y sostenibles.');
    });
  }

  // Metadatos extendidos por categoria de producto
  var metaProductos = [
    {
      icono: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/></svg>',
      color: { hex: '#C1121F', rgb: '193,18,31' },
      accion: 'Ver los 48 colores',
      destino: 'colores',
      etiqueta: '48 colores disponibles'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
      color: { hex: '#0573BC', rgb: '5,115,188' },
      accion: 'Ver equipos',
      destino: 'equipos',
      etiqueta: '15 equipos y repuestos'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
      color: { hex: '#2D8A4E', rgb: '45,138,78' },
      accion: 'Cotizar repuestos',
      destino: 'cotizacion',
      etiqueta: 'Envio nacional'
    }
  ];

  var pro = $('#lista-productos');
  D.productos.forEach(function (p, idx) {
    var meta = metaProductos[idx] || { icono: '', color: { hex: '#C1121F', rgb: '193,18,31' }, accion: 'Ver mas', destino: '', etiqueta: '' };
    var art = document.createElement('article');
    art.className = 'producto';
    art.setAttribute('tabindex', '0');
    art.setAttribute('role', 'region');
    art.style.setProperty('--prod-color', meta.color.hex);
    art.style.setProperty('--prod-sombra', 'rgba(' + meta.color.rgb + ', 0.18)');
    art.style.setProperty('--prod-fondo', 'rgba(' + meta.color.rgb + ', 0.07)');

    // Cabecera: icono + etiqueta de categoria
    var cab = document.createElement('div');
    cab.className = 'producto-cab';
    var icoWrap = document.createElement('div');
    icoWrap.className = 'producto-icono';
    icoWrap.setAttribute('aria-hidden', 'true');
    icoWrap.innerHTML = meta.icono;
    var etq = document.createElement('span');
    etq.className = 'producto-etiqueta';
    etq.textContent = meta.etiqueta;
    cab.appendChild(icoWrap);
    cab.appendChild(etq);
    art.appendChild(cab);

    // Titulo
    var h = document.createElement('h3');
    h.className = 'producto-titulo';
    h.textContent = p[0];
    art.appendChild(h);

    // Chips de caracteristicas
    var chips = document.createElement('ul');
    chips.className = 'producto-chips';
    p[1].forEach(function (t) {
      var li = document.createElement('li');
      li.className = 'producto-chip';
      li.textContent = t;
      chips.appendChild(li);
    });
    art.appendChild(chips);

    // Boton de accion
    var pie = document.createElement('div');
    pie.className = 'producto-pie';
    var btn = document.createElement('button');
    btn.className = 'btn btn-producto';
    btn.innerHTML = meta.accion + ' <i aria-hidden="true">&rarr;</i>';
    btn.addEventListener('click', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: meta.color.hex, rgb: meta.color.rgb }, 24);
      if (meta.destino === 'cotizacion') {
        var btnCot = $$('[data-abrir-cotizacion]')[0];
        if (btnCot) btnCot.click();
      } else {
        var sec = document.getElementById(meta.destino);
        if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
    pie.appendChild(btn);
    art.appendChild(pie);

    // Hover: disparo suave de chorro
    art.addEventListener('mouseenter', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: meta.color.hex, rgb: meta.color.rgb }, 12);
    });

    pro.appendChild(art);
  });

  // Metadatos extendidos por servicio
  var metaServicios = [
    {
      icono: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
      color: { hex: '#0573BC', rgb: '5,115,188' },
      etiqueta: 'Consultoria',
      numero: '01'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
      color: { hex: '#D96B27', rgb: '217,107,39' },
      etiqueta: 'Capacitacion',
      numero: '02'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
      color: { hex: '#2D8A4E', rgb: '45,138,78' },
      etiqueta: 'Instalacion',
      numero: '03'
    },
    {
      icono: '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
      color: { hex: '#7C649D', rgb: '124,100,157' },
      etiqueta: 'Optimizacion',
      numero: '04'
    }
  ];

  var srv = $('#lista-servicios');
  D.servicios.forEach(function (s, i) {
    var meta = metaServicios[i] || { icono: '', color: { hex: '#C1121F', rgb: '193,18,31' }, etiqueta: 'Servicio', numero: '0' + (i+1) };
    var art = document.createElement('article');
    art.className = 'servicio';
    art.setAttribute('tabindex', '0');
    art.style.setProperty('--srv-color', meta.color.hex);
    art.style.setProperty('--srv-sombra', 'rgba(' + meta.color.rgb + ', 0.20)');
    art.style.setProperty('--srv-fondo',  'rgba(' + meta.color.rgb + ', 0.07)');

    // Cabecera: numero + icono + etiqueta
    var cab = document.createElement('div');
    cab.className = 'servicio-cab';

    var num = document.createElement('span');
    num.className = 'servicio-numero';
    num.textContent = meta.numero;

    var icoWrap = document.createElement('div');
    icoWrap.className = 'servicio-icono';
    icoWrap.setAttribute('aria-hidden', 'true');
    icoWrap.innerHTML = meta.icono;

    var etq = document.createElement('span');
    etq.className = 'servicio-etiqueta';
    etq.textContent = meta.etiqueta;

    cab.appendChild(num);
    cab.appendChild(icoWrap);
    cab.appendChild(etq);
    art.appendChild(cab);

    // Titulo
    var h = document.createElement('h3');
    h.className = 'servicio-titulo';
    h.textContent = s[0];
    art.appendChild(h);

    // Chips de detalle
    if (s[1] && s[1].length) {
      var chips = document.createElement('ul');
      chips.className = 'servicio-chips';
      s[1].forEach(function (t) {
        var li = document.createElement('li');
        li.className = 'servicio-chip';
        li.textContent = t;
        chips.appendChild(li);
      });
      art.appendChild(chips);
    }

    // Boton agregar a cotizacion
    var pie = document.createElement('div');
    pie.className = 'servicio-pie';
    var b = document.createElement('button');
    b.className = 'btn btn-servicio agregar';
    b.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Agregar a la cotizaci\u00f3n';
    b.addEventListener('click', function () {
      sumar('servicio', i);
      pintarCarrito();
      avisar('"' + s[0] + '" agregada');
      if (dispararChorroPistola) dispararChorroPistola({ hex: meta.color.hex, rgb: meta.color.rgb }, 18);
    });
    pie.appendChild(b);
    art.appendChild(pie);

    // Hover: disparo suave
    art.addEventListener('mouseenter', function () {
      if (dispararChorroPistola) dispararChorroPistola({ hex: meta.color.hex, rgb: meta.color.rgb }, 10);
    });

    srv.appendChild(art);
  });

  // ---------------------------------------------------------------- contacto
  var icoContacto = {
    ubicacion: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    whatsapp:  '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.127.558 4.126 1.532 5.859L.054 23.428a.5.5 0 0 0 .612.612l5.568-1.478A11.944 11.944 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.891 0-3.667-.523-5.183-1.432l-.361-.215-3.744.993.993-3.744-.216-.361A9.944 9.944 0 0 1 2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>',
    horario:   '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    instagram: '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>',
    facebook:  '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.235 2.686.235v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.268h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/></svg>',
    youtube:   '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M23.495 6.205a3.007 3.007 0 0 0-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 0 0 .527 6.205a31.247 31.247 0 0 0-.522 5.805 31.247 31.247 0 0 0 .522 5.783 3.007 3.007 0 0 0 2.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 0 0 2.088-2.088 31.247 31.247 0 0 0 .5-5.783 31.247 31.247 0 0 0-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/></svg>',
    tiktok:    '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>'
  };

  var colorRedes = {
    instagram: '#E1306C',
    facebook:  '#1877F2',
    youtube:   '#FF0000',
    tiktok:    '#010101'
  };

  function linea(rotulo, valor, href, tipoIcono, colorIcono) {
    var d = document.createElement('div');
    d.className = 'dato';
    if (colorIcono) {
      d.style.setProperty('--dato-color', colorIcono);
      d.style.setProperty('--dato-fondo', colorIcono.replace(')', ', 0.08)').replace('rgb', 'rgba').replace('#', 'rgba(').replace('rgba(#', 'rgba('));
    }

    var cab = document.createElement('div');
    cab.className = 'dato-cab';

    if (tipoIcono && icoContacto[tipoIcono]) {
      var ico = document.createElement('span');
      ico.className = 'dato-icono';
      ico.setAttribute('aria-hidden', 'true');
      ico.innerHTML = icoContacto[tipoIcono];
      cab.appendChild(ico);
    }

    var rot = document.createElement('span');
    rot.className = 'dato-rotulo';
    rot.textContent = rotulo;
    cab.appendChild(rot);
    d.appendChild(cab);

    var val = document.createElement(href ? 'a' : 'strong');
    val.className = 'dato-valor';
    if (href) { val.href = href; val.target = '_blank'; val.rel = 'noopener noreferrer'; }
    val.textContent = valor;
    d.appendChild(val);
    return d;
  }

  // URLs de redes sociales
  var urlsRedes = {
    'Instagram': 'https://instagram.com/jathelectroestatic',
    'Facebook':  'https://facebook.com/jathelectroestatic',
    'YouTube':   'https://youtube.com/@jathelectroestatic',
    'TikTok':    'https://tiktok.com/@jathelectroestatic'
  };

  var cd = $('#contacto-datos');

  // Datos principales
  var datosPrin = document.createElement('div');
  datosPrin.className = 'contacto-datos-principal';
  datosPrin.appendChild(linea('Ubicaci\u00f3n', D.contacto.ubicacion, null, 'ubicacion', '#C1121F'));
  datosPrin.appendChild(linea('WhatsApp', D.contacto.whatsapp, 'https://wa.me/' + D.contacto.whatsapp_numero, 'whatsapp', '#25D366'));
  datosPrin.appendChild(linea('Horario', D.contacto.horario, null, 'horario', '#0573BC'));
  cd.appendChild(datosPrin);

  // Redes sociales
  if (D.contacto.redes && D.contacto.redes.length) {
    var redesTit = document.createElement('p');
    redesTit.className = 'contacto-redes-titulo';
    redesTit.textContent = 'S\u00edguenos';
    cd.appendChild(redesTit);

    var redesGrid = document.createElement('div');
    redesGrid.className = 'contacto-redes';
    D.contacto.redes.forEach(function (r) {
      var nombre = r[0];
      var tipoKey = nombre.toLowerCase();
      var color = colorRedes[tipoKey] || '#6E6862';
      var url = urlsRedes[nombre] || null;
      var btn = document.createElement(url ? 'a' : 'div');
      btn.className = 'red-social';
      btn.style.setProperty('--red-color', color);
      if (url) { btn.href = url; btn.target = '_blank'; btn.rel = 'noopener noreferrer'; }

      var icoSpan = document.createElement('span');
      icoSpan.className = 'red-icono';
      icoSpan.setAttribute('aria-hidden', 'true');
      icoSpan.innerHTML = icoContacto[tipoKey] || '';

      var nomSpan = document.createElement('span');
      nomSpan.className = 'red-nombre';
      nomSpan.textContent = nombre;

      var handleSpan = document.createElement('span');
      handleSpan.className = 'red-handle';
      handleSpan.textContent = r[1];

      btn.appendChild(icoSpan);
      btn.appendChild(nomSpan);
      btn.appendChild(handleSpan);
      redesGrid.appendChild(btn);
    });
    cd.appendChild(redesGrid);
  }

  // ---------------------------------------------------------------- colores
  var acabadoActual = 'todos';
  var busqueda = '';

  function pintarFiltrosColor() {
    var caja = $('#filtros-color');
    caja.innerHTML = '';
    var lista = [{ nombre: 'todos', cuenta: D.colores.length }];
    D.acabados.forEach(function (a) {
      lista.push({ nombre: a, cuenta: D.colores.filter(function (c) { return c.acabado === a; }).length });
    });
    lista.forEach(function (a) {
      if (!a.cuenta) return;
      var b = document.createElement('button');
      b.className = 'chip';
      b.type = 'button';
      b.setAttribute('aria-pressed', String(acabadoActual === a.nombre));
      b.textContent = a.nombre === 'todos' ? 'Todos' : a.nombre + ' (' + a.cuenta + ')';
      b.addEventListener('click', function () {
        acabadoActual = a.nombre;
        pintarFiltrosColor();
        pintarColores();
      });
      caja.appendChild(b);
    });
  }

  function enCotizacion(tipo, id) {
    return carrito.some(function (i) { return i.tipo === tipo && i.id === id; });
  }

  function pintarColores() {
    var rej = $('#rejilla-colores');
    rej.innerHTML = '';
    var q = busqueda.replace(/^#/, '').toUpperCase();
    var lista = D.colores.filter(function (c) {
      if (acabadoActual !== 'todos' && c.acabado !== acabadoActual) return false;
      if (!q) return true;
      return c.nombre.toUpperCase().indexOf(q) >= 0
          || c.acabado.toUpperCase().indexOf(q) >= 0
          || c.hex.replace('#', '').toUpperCase().indexOf(q) === 0;
    });
    $('#color-vacio').hidden = lista.length > 0;
    lista.forEach(function (c) {
      var art = document.createElement('article');
      art.className = 'muestra' + (enCotizacion('color', c.id) ? ' muestra-elegida' : '');

      var bloque = document.createElement('div');
      bloque.className = 'muestra-color';
      bloque.style.background = c.hex;
      art.appendChild(bloque);

      var datos = document.createElement('div');
      datos.className = 'muestra-datos';
      var nom = document.createElement('div');
      nom.className = 'muestra-nombre';
      nom.textContent = c.nombre;
      var hex = document.createElement('div');
      hex.className = 'muestra-hex';
      hex.textContent = c.hex + ' · ' + c.acabado;
      var acc = document.createElement('div');
      acc.className = 'muestra-acciones';

      var ver = document.createElement('button');
      ver.type = 'button';
      ver.textContent = 'Ver';
      ver.addEventListener('click', function () { abrirLupa(c); });

      var add = document.createElement('button');
      add.type = 'button';
      add.className = 'agregar';
      add.textContent = enCotizacion('color', c.id) ? 'Agregado' : '+ Agregar';
      add.addEventListener('click', function () {
        sumar('color', c.id);
        pintarColores();
        pintarCarrito();
        avisar(c.hex + ' agregado');
      });

      acc.appendChild(ver);
      acc.appendChild(add);
      datos.appendChild(nom);
      datos.appendChild(hex);
      if (c.revisar) {
        var rev = document.createElement('div');
        rev.className = 'muestra-revisar';
        rev.textContent = 'nombre por confirmar';
        datos.appendChild(rev);
      }
      datos.appendChild(acc);
      art.appendChild(datos);
      rej.appendChild(art);
    });
  }

  $('#buscar-color').addEventListener('input', function (e) {
    busqueda = e.target.value;
    pintarColores();
  });

  // ---------------------------------------------------------------- lupa de color
  var lupaActual = null;
  function abrirLupa(c) {
    lupaActual = c;
    $('#lupa-color').style.background = c.hex;
    $('#lupa-familia').textContent = c.nombre;
    $('#lupa-hex').textContent = c.hex;
    $('#lupa-rgb').textContent = c.acabado + ' · ' + c.rgb_texto;
    $('#lupa-nota').textContent =
      'Color ' + c.hex + ' de la carta ' + (c.carta === 3 ? '1' : '2') +
      ', fila ' + c.fila + ', columna ' + c.col + ', acabado ' + c.acabado +
      '. El código se lo puede dar a cualquier proveedor de powder coating.';
    $('#lupa-agrregar').textContent = enCotizacion('color', c.id) ? 'Agregar otra vez' : 'Agregar a la cotización';
    // Mirar una carta impresa esconde este boton, asi que hay que volverlo a mostrar. Si no,
    // despues de mirar una carta el boton quedaba muerto para el resto de la sesion.
    $('#lupa-agrregar').hidden = false;
    $('#lupa').hidden = false;
  }
  function cerrarLupa() { $('#lupa').hidden = true; lupaActual = null; }
  $$('[data-cerrar-lupa]').forEach(function (b) { b.addEventListener('click', cerrarLupa); });
  $('#lupa-agrregar').addEventListener('click', function () {
    if (!lupaActual) return;
    sumar('color', lupaActual.id);
    pintarColores();
    pintarCarrito();
    avisar(lupaActual.hex + ' agregado');
    cerrarLupa();
  });
  $('#lupa-copiar').addEventListener('click', function () {
    if (!lupaActual) return;
    copiar(lupaActual.hex + '  ' + lupaActual.rgb_texto);
  });

  // ---------------------------------------------------------------- equipos
  var catActual = 'todas';
  function pintarFiltrosEquipo() {
    var caja = $('#filtros-equipo');
    caja.innerHTML = '';
    var cats = [{ nombre: 'todas', cuenta: D.equipos.length }];
    D.equipos.forEach(function (e) {
      var c = null;
      for (var i = 0; i < cats.length; i++) { if (cats[i].nombre === e.categoria) c = cats[i]; }
      if (c) c.cuenta += 1; else cats.push({ nombre: e.categoria, cuenta: 1 });
    });
    cats.forEach(function (c) {
      var b = document.createElement('button');
      b.className = 'chip';
      b.type = 'button';
      b.setAttribute('aria-pressed', String(catActual === c.nombre));
      b.textContent = c.nombre === 'todas' ? 'Todos' : c.nombre + ' (' + c.cuenta + ')';
      b.addEventListener('click', function () {
        catActual = c.nombre;
        pintarFiltrosEquipo();
        pintarEquipos();
      });
      caja.appendChild(b);
    });
  }

  function tarjetaEquipo(e) {
    var art = document.createElement('article');
    art.className = 'equipo';

    var foto = document.createElement('div');
    foto.className = 'equipo-foto';
    var img = document.createElement('img');
    img.src = e.archivo;
    img.alt = e.nombre;
    img.loading = 'lazy';
    img.decoding = 'async';
    foto.appendChild(img);
    art.appendChild(foto);

    var cuerpo = document.createElement('div');
    cuerpo.className = 'equipo-cuerpo';
    var cat = document.createElement('div');
    cat.className = 'equipo-cat';
    cat.textContent = e.categoria;
    var nom = document.createElement('div');
    nom.className = 'equipo-nombre';
    nom.textContent = e.nombre;
    cuerpo.appendChild(cat);
    cuerpo.appendChild(nom);
    if (e.provisional) {
      var pr = document.createElement('div');
      pr.className = 'provisional';
      pr.textContent = 'Nombre provisional';
      cuerpo.appendChild(pr);
    }

    var acc = document.createElement('div');
    acc.className = 'equipo-acciones';
    var add = document.createElement('button');
    add.type = 'button';
    add.className = 'agregar';
    add.textContent = enCotizacion('equipo', e.id) ? 'Agregado' : '+ Agregar';
    add.addEventListener('click', function () {
      sumar('equipo', e.id);
      pintarEquipos();
      pintarCarrito();
      avisar('"' + e.nombre + '" agregado');
    });
    acc.appendChild(add);
    cuerpo.appendChild(acc);
    art.appendChild(cuerpo);
    return art;
  }

  function pintarEquipos() {
    var rej = $('#rejilla-equipos');
    rej.innerHTML = '';
    D.equipos.filter(function (e) {
      return catActual === 'todas' || e.categoria === catActual;
    }).forEach(function (e) { rej.appendChild(tarjetaEquipo(e)); });
  }

  // ---------------------------------------------------------------- carta impresa
  $$('.carta').forEach(function (b) {
    b.addEventListener('click', function () {
      abrirLupa({
        hex: 'Carta impresa', rgb_texto: b.getAttribute('data-carta'),
        nombre: 'Carta impresa', acabado: 'Así se ve en el papel', carta: 3, fila: 0, col: 0
      });
      var img = new Image();
      img.src = b.getAttribute('data-carta');
      $('#lupa-color').style.background = '#fff url("' + b.getAttribute('data-carta') + '") center/contain no-repeat';
      $('#lupa-hex').textContent = 'Carta impresa';
      $('#lupa-rgb').textContent = 'Tono real de la muestra';
      $('#lupa-nota').textContent =
        'Esta es la carta tal como se imprime. El color de pantalla no es confiable: pida una muestra física.';
      $('#lupa-agrregar').hidden = true;
    });
  });

  // ---------------------------------------------------------------- cotizador
  function nombreDe(item) {
    if (item.tipo === 'color')  { var c = colorPorId[item.id];  return c ? c.nombre : 'Color'; }
    if (item.tipo === 'equipo') { var e = equipoPorId[item.id]; return e ? e.nombre : 'Equipo'; }
    return D.servicios[item.id] ? D.servicios[item.id][0] : 'Servicio';
  }
  function detalleDe(item) {
    if (item.tipo === 'color')  { var c = colorPorId[item.id];  return c ? c.rgb_texto : ''; }
    if (item.tipo === 'equipo') { var e = equipoPorId[item.id]; return e ? e.categoria : ''; }
    return 'Servicio';
  }

  function pintarCarrito() {
    var ul = $('#cajon-lista');
    ul.innerHTML = '';
    $('#cajon-vacio').hidden = carrito.length > 0;

    carrito.forEach(function (item) {
      var li = document.createElement('li');

      if (item.tipo === 'color') {
        var m = document.createElement('div');
        m.className = 'cajon-muestra';
        m.style.background = colorPorId[item.id].hex;
        li.appendChild(m);
      } else if (item.tipo === 'equipo') {
        var im = document.createElement('img');
        im.className = 'cajon-foto';
        im.src = equipoPorId[item.id].archivo;
        im.alt = '';
        li.appendChild(im);
      }

      var txt = document.createElement('div');
      txt.className = 'cajon-txt';
      var n = document.createElement('div');
      n.className = 'cajon-nom';
      n.textContent = nombreDe(item);
      var d = document.createElement('div');
      d.className = 'cajon-det';
      d.textContent = detalleDe(item);
      txt.appendChild(n);
      txt.appendChild(d);
      li.appendChild(txt);

      var can = document.createElement('div');
      can.className = 'cantidad';
      var menos = document.createElement('button');
      menos.type = 'button';
      menos.textContent = '−';
      menos.setAttribute('aria-label', 'Quitar uno');
      var num = document.createElement('span');
      num.textContent = String(item.cantidad);
      var mas = document.createElement('button');
      mas.type = 'button';
      mas.textContent = '+';
      mas.setAttribute('aria-label', 'Agregar uno');
      menos.addEventListener('click', function () {
        restar(item.tipo, item.id); pintarCarrito(); pintarColores(); pintarEquipos();
      });
      mas.addEventListener('click', function () {
        sumar(item.tipo, item.id); pintarCarrito(); pintarColores(); pintarEquipos();
      });
      can.appendChild(menos);
      can.appendChild(num);
      can.appendChild(mas);
      li.appendChild(can);

      var x = document.createElement('button');
      x.className = 'cajon-quitar';
      x.type = 'button';
      x.textContent = '×';
      x.setAttribute('aria-label', 'Quitar ' + nombreDe(item));
      x.addEventListener('click', function () {
        quitar(item.tipo, item.id); pintarCarrito(); pintarColores(); pintarEquipos();
      });
      li.appendChild(x);
      ul.appendChild(li);
    });

    var t = total();
    var barra = $('#barra');
    barra.hidden = t === 0;
    $('#abrir-cotizacion').hidden = t === 0;
    document.body.classList.toggle('sin-barra', t === 0);
    $('#barra-cuenta').textContent = String(t);
    $('#barra-texto').textContent = t === 1 ? 'item en su cotización' : 'items en su cotización';
    $('#boton-whatsapp').classList.toggle('btn-rojo', t > 0);
    $('#cajon-riesgo').hidden = t === 0;

    guardar(carrito);
  }

  function mensaje() {
    var l = [];
    l.push('Hola. Quiero cotizar lo siguiente con JATH ELECTROESTATIC:');
    l.push('');
    var cols = carrito.filter(function (i) { return i.tipo === 'color'; });
    var eqs  = carrito.filter(function (i) { return i.tipo === 'equipo'; });
    var svs  = carrito.filter(function (i) { return i.tipo === 'servicio'; });

    if (cols.length) {
      l.push('*COLORES* (nombre y código de la carta)');
      cols.forEach(function (i) {
        var c = colorPorId[i.id];
        l.push('• ' + c.nombre + '  ' + c.hex + '  ' + c.rgb_texto + '  x' + i.cantidad);
      });
      l.push('');
    }
    if (eqs.length) {
      l.push('*EQUIPOS Y REPUESTOS*');
      eqs.forEach(function (i) {
        l.push('• ' + equipoPorId[i.id].nombre + '  x' + i.cantidad +
               '  (' + equipoPorId[i.id].categoria + ')');
      });
      l.push('');
    }
    if (svs.length) {
      l.push('*SERVICIOS*');
      svs.forEach(function (i) {
        l.push('• ' + D.servicios[i.id][0] + '  x' + i.cantidad);
      });
      l.push('');
    }
    var nota = $('#nota').value.trim();
    if (nota) { l.push('*COMENTARIO*'); l.push(nota); l.push(''); }

    l.push('Enviado desde el catálogo de JATH ELECTROESTATIC.');
    return l.join('\n');
  }

  function pintarEnlaces() {
    var txt = mensaje();
    var href = WA + '?text=' + encodeURIComponent(txt);
    $('#boton-whatsapp').href = href;
    $('#wa-fijo').href = WA;
  }
  $('#nota').addEventListener('input', pintarEnlaces);

  function copiar(txt) {
    function ok() { avisar('Copiado: ' + txt); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(ok, function () { respaldo(txt, ok); });
    } else { respaldo(txt, ok); }
  }
  function respaldo(txt, ok) {
    var ta = document.createElement('textarea');
    ta.value = txt;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); ok(); } catch (e) { avisar('No se pudo copiar'); }
    document.body.removeChild(ta);
  }
  // ---------------------------------------------------------------- cajon
  function abrirCajon() {
    $('#cajon').hidden = false;
    $('#velo').hidden = false;
    pintarCarrito();
    pintarEnlaces();
  }
  function cerrarCajon() { $('#cajon').hidden = true; $('#velo').hidden = true; }
  $('#abrir-cotizacion').addEventListener('click', abrirCajon);
  $('#cerrar-cajon').addEventListener('click', cerrarCajon);
  $$('[data-abrir-cotizacion]').forEach(function (b) { b.addEventListener('click', abrirCajon); });
  $('#velo').addEventListener('click', cerrarCajon);
  $$('[data-ir]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = document.getElementById(b.getAttribute('data-ir'));
      if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (!$('#lupa').hidden) { cerrarLupa(); return; }
    if (!$('#cajon').hidden) cerrarCajon();
  });

  // ---------------------------------------------------------------- arranque
  pintarFiltrosColor();
  pintarColores();
  pintarFiltrosEquipo();
  pintarEquipos();
  pintarCarrito();
  pintarEnlaces();
}());
