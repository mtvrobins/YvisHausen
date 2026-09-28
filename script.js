// ---------- Loader (index page only) ----------
// The coin is a still PNG; on top of it a small WebGL pass sets it alight:
// liquid-metal fire catches at the tail, climbs up behind the body and is
// drawn up into the flame-shaped inflections above the wings, passing behind
// the raised relief and lettering. The bird's head turns gently.
const LOADER_MS = 4600;
let stopCoinFire = null;

window.addEventListener('load', () => {
  const loader = document.getElementById('loader');
  if(!loader) return;
  stopCoinFire = startCoinFire(loader.querySelector('.loader-coin-fire'));
  setTimeout(() => {
    loader.classList.add('hide');
    setTimeout(() => { if(stopCoinFire) stopCoinFire(); }, 1000);
  }, LOADER_MS);
});

function startCoinFire(canvas){
  if(!canvas) return null;
  // with reduced motion, draw a single finished frame instead of animating
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const gl = canvas.getContext('webgl', { premultipliedAlpha:true, alpha:true, antialias:false });
  if(!gl) return null;

  const vs = 'attribute vec2 p; varying vec2 uv; void main(){ uv = p * vec2(0.5, -0.5) + 0.5; gl_Position = vec4(p, 0.0, 1.0); }';
  const fs = `
    precision mediump float;
    varying vec2 uv;
    uniform sampler2D coin;    // the finished medal
    uniform sampler2D flames;  // r: where fire may burn, g: raised relief it passes behind, b: head weight
    uniform float t;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float noise(vec2 p){
      vec2 i = floor(p), f = fract(p);
      vec2 u = f * f * (3.0 - 2.0 * f);
      return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
                 mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
    }
    float fbm(vec2 p){ return 0.65 * noise(p) + 0.35 * noise(p * 2.07 + 5.3); }
    // liquid-metal flame: a slowly warping field whose ridges are drawn upward
    float flame(vec2 p){
      vec2 w = vec2(fbm(p * vec2(3.0, 2.0) + vec2(0.0, t * 0.5)),
                    fbm(p * vec2(3.0, 2.0) + vec2(4.7, t * 0.5 + 2.3)));
      vec2 q = vec2(p.x * 12.0 + (w.x - 0.5) * 3.2, p.y * 3.6 + t * 0.95 + (w.y - 0.5) * 1.4);
      float r = 1.0 - abs(fbm(q) * 2.0 - 1.0);
      return smoothstep(0.35, 1.0, r);
    }
    void main(){
      vec3 m = texture2D(flames, uv).rgb;
      vec2 st = uv;
      // the head turns gently about the middle of the neck
      if(m.b > 0.001){
        vec2 piv = vec2(0.5207, 0.2563);
        // ...and towards the end bows a little further down
        float dip = smoothstep(2.6, 3.9, t);
        float a = ((0.014 * sin(t * 0.9) + 0.005 * sin(t * 1.9 + 1.0)) * (1.0 - 0.5 * dip) - 0.035 * dip) * m.b;
        vec2 d = uv - piv;
        st = piv + vec2(d.x * cos(a) - d.y * sin(a), d.x * sin(a) + d.y * cos(a));
        st.y -= 0.004 * dip * m.b;
      }
      vec4 c = texture2D(coin, st);
      if(m.r > 0.001){
        // ignition: the fire catches at the bottom and climbs with a ragged,
        // flickering edge, then keeps being drawn up through the wings
        float yb = 1.0 - uv.y;
        float rag = (noise(vec2(uv.x * 9.0, t * 1.6)) - 0.5) * 0.14;
        float front = t * 0.42 + 0.02;
        float lit = 1.0 - smoothstep(front - 0.12, front + 0.02, yb + rag);
        // quieter and more transparent low down, fuller towards the wings
        float low = mix(0.28, 1.0, smoothstep(0.12, 0.55, yb));
        float k = m.r * lit * (1.0 - m.g) * low;
        if(k > 0.001){
          float e = 0.003;
          float h = flame(uv);
          float hx = flame(uv + vec2(e, 0.0)), hy = flame(uv + vec2(0.0, e));
          float s = 0.011 * k;
          vec3 n = normalize(vec3(-(hx - h) / e * s, -(hy - h) / e * s, 1.0));
          vec3 L = normalize(vec3(-0.5, -0.62, 0.6));
          vec3 H = normalize(L + vec3(0.0, 0.0, 1.0));
          float diff = dot(n, L) - L.z;
          float spec = max(pow(max(dot(n, H), 0.0), 32.0) - pow(H.z, 32.0), 0.0);
          // a soft bright seam where the fire is catching
          float seam = exp(-pow((yb + rag - front) / 0.035, 2.0)) * m.r * (1.0 - m.g) * low * step(front, 1.15);
          c.rgb *= 1.0 + diff * 1.0 + h * k * 0.12 + seam * 0.25;
          c.rgb += (c.rgb * 0.6 + 0.2) * spec * 1.4;
        }
      }
      gl_FragColor = vec4(c.rgb * c.a, c.a);
    }`;

  function shader(type, src){
    const sh = gl.createShader(type); gl.shaderSource(sh, src); gl.compileShader(sh);
    return gl.getShaderParameter(sh, gl.COMPILE_STATUS) ? sh : null;
  }
  const v = shader(gl.VERTEX_SHADER, vs), f = shader(gl.FRAGMENT_SHADER, fs);
  if(!v || !f) return null;
  const prog = gl.createProgram();
  gl.attachShader(prog, v); gl.attachShader(prog, f); gl.linkProgram(prog);
  if(!gl.getProgramParameter(prog, gl.LINK_STATUS)) return null;
  gl.useProgram(prog);

  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  function texture(unit, name, src){
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => { try {
        gl.activeTexture(gl.TEXTURE0 + unit);
        gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.uniform1i(gl.getUniformLocation(prog, name), unit);
        resolve();
      } catch(e){ reject(e); } };
      img.onerror = reject;
      img.src = src;
    });
  }

  const tLoc = gl.getUniformLocation(prog, 't');
  let raf = 0, running = true;
  const t0 = performance.now();
  function frame(now){
    if(!running) return;
    const size = Math.round(canvas.clientWidth * Math.min(window.devicePixelRatio || 1, 2));
    if(canvas.width !== size){ canvas.width = canvas.height = size; gl.viewport(0, 0, size, size); }
    gl.uniform1f(tLoc, still ? 6.0 : (now - t0) / 1000);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if(!still) raf = requestAnimationFrame(frame);
  }
  Promise.all([texture(0, 'coin', 'images/yvis-hausen-coin.png'),
               texture(1, 'flames', 'images/coin-flames.png')])
    .then(() => { if(running) raf = requestAnimationFrame(frame); })
    .catch(() => {});
  return () => { running = false; cancelAnimationFrame(raf); };
}

// ---------- i18n ----------
const SUBTITLES = {
  en: ["International Creative House","Global Ideation Firm","Global Meta Acquisition","Private Art Office","Artist Agency","Brand Governance"],
  fr: ["Maison Créative Internationale","Cabinet d'Idéation Global","Acquisition Meta Mondiale","Bureau d'Art Privé","Agence d'Artistes","Gouvernance de Marque"],
  it: ["Casa Creativa Internazionale","Studio di Ideazione Globale","Acquisizione Meta Globale","Ufficio d'Arte Privato","Agenzia di Artisti","Governance del Brand"]
};

const I18N = {
  en: {
    enquire_btn:"ENQUIRE",
    lang_label:"LANGUAGE", lang_option_en:"English", lang_option_fr:"French", lang_option_it:"Italian",
    group_creative:"CREATIVE HOUSE", group_curation:"CURATION", group_art:"ART & CULTURAL",
    cat_sound_label:"SOUND ARCHITECTURE", cat_sound_desc:"Original Compositions — Fashion Runway Scores, Sonic Identities, Film Scores, Immersive Soundscapes",
    cat_visual_label:"VISUAL DIRECTION", cat_visual_desc:"Bespoke visual design for fashion, events and brands — Event Invitation Design, Editorial & Print, Menu Design, Magazine & Publication",
    cat_sceno_label:"SCENOGRAPHY", cat_sceno_desc:"Spatial worlds, sets and environments created for fashion, film, exhibitions and cultural experiences",
    cat_talent_label:"TALENT PORTFOLIOS", cat_talent_desc:"Casting talents for Fashion and Film.",
    cat_event_label:"EVENT CURATION", cat_event_desc:"Bespoke environments, gatherings and experiences for brands, institutions and private clients",
    cat_exhib_label:"EXHIBITIONS", cat_exhib_desc:"Curation and presentation of exhibitions for institutions, galleries and private collections",
    cat_art_label:"PRIVATE ART", cat_art_desc:"Private Art Advisory & Art Sourcing — Research, sourcing, curation and acquisition support for private collections",
    footer_line:"YVIS HAUSEN  —  PRIVATE PRACTICE  —  BY INQUIRY ONLY",

    tile_ops_title:"OPERATIONS", tile_mkt_link:"MARKETING",
    tile_mkt_desc:"Meta Ads, Brand Governance, Promotion.",
    tile_talent_title:"TALENT REPRESENTATION", tile_talent_link1:"TALENT",
    tile_talent_link1_desc:"Casting talents for Fashion and Film.", tile_talent_link2:"AGENTS",
    tile_talent_link2_desc:"Representation, placement and career management across fashion and film.",
    tile_creative_title:"CREATIVE HOUSE",
    tile_art_title:"ART & CULTURE",

    db_heading_title:"YVIS HAUSEN DATABASE", db_heading_sub:"PROJECT FILING SYSTEM",
    code_label:"PRIVATE CODE", code_cancel:"CANCEL", code_error:"ACCESS DENIED", code_restricted:"ACCESS RESTRICTED. ACCESS CODES ARE PROVIDED BY AUTHORISED AGENTS ONLY",
    db_eyebrow:"PROJECT DATABASE: PORTFOLIO", db_404:"404 ERROR",

    page_sound_title:"Sound Architecture", page_sound_lede:"Composition as a spatial and sensory language.",
    page_sound_p1:"Yvis Hausen creates original sound for fashion, film and immersive environments — work built to be felt as much as heard, shaping mood, pace and memory within a space or a story.",
    page_sound_p2:"Our compositions are developed specifically for runway, screen and installation, translating a brand's identity or a director's vision into sonic form.",
    page_sound_p3:"Current work is undertaken privately and by commission, in close collaboration with the creative teams behind each project.",

    page_visual_title:"Visual Direction", page_visual_lede:"Considered design across fashion, brand and print.",
    page_visual_p1:"We create bespoke visual work for fashion houses, events and institutions — from event invitations and editorial layouts to menus and publication design.",
    page_visual_p2:"Each commission is treated as its own design problem, built from the language of the brand or occasion it serves rather than a fixed house style.",
    page_visual_p3:"Recent focus includes refined, minimal menu design — treating the printed page with the same precision as a runway invitation.",

    page_sceno_title:"Scenography", page_sceno_lede:"Spatial worlds for fashion, film and exhibition.",
    page_sceno_p1:"Yvis Hausen designs sets and environments for fashion presentations, film production, exhibitions and cultural experiences — spaces built to carry a narrative.",
    page_sceno_p2:"Our approach treats scenography as storytelling in three dimensions, shaping how an audience moves through and experiences a moment.",
    page_sceno_p3:"Work is developed privately, in collaboration with directors, curators and brand teams.",

    page_talent_title:"Talent Representation", page_talent_lede:"Casting talents for Fashion and Film.",
    page_talent_p1:"We identify, represent and place talent across fashion and film, working closely with casting directors, brands and production teams.",
    page_talent_p2:"Our roster is developed selectively, with an emphasis on presence, versatility and a distinctive point of view.",
    page_talent_p3:"Enquiries regarding representation or casting are handled privately.",

    page_event_title:"Event Curation", page_event_lede:"Bespoke gatherings, considered from first idea to final detail.",
    page_event_p1:"Yvis Hausen curates environments, gatherings and experiences for brands, institutions and private clients — occasions built around a clear idea rather than a template.",
    page_event_p2:"We work across concept, spatial design, guest experience and atmosphere, shaping each detail toward a single considered outcome.",
    page_event_p3:"Current work is undertaken privately and by introduction.",

    page_exhib_title:"Exhibitions", page_exhib_lede:"Cultural presentations, shaped with intention.",
    page_exhib_p1:"We develop and curate exhibitions for cultural institutions, galleries and private collections — translating a body of work or an idea into a considered spatial experience.",
    page_exhib_p2:"Our approach spans concept, layout and presentation, working closely with artists, curators and institutions to shape how work is encountered.",
    page_exhib_p3:"Enquiries regarding exhibition curation are welcomed privately.",

    page_art_title:"Art & Cultural Advisory",
    page_art_p1:"Yvis Hausen is developing a private art advisory practice focused on the discovery, sourcing and placement of exceptional works across contemporary art and visual culture.",
    page_art_p2:"As our other work in the Creative House sector increasingly intersected with artists, collectors, designers and cultural institutions, we began developing a dedicated Art & Cultural Advisory practice. Our approach is intentionally selective, connecting artists, collectors, creative institutions and luxury environments through considered introductions and bespoke sourcing.",
    page_art_p3:"We are currently developing relationships with artists, galleries, collectors and private clients ahead of the formal launch of the practice.",
    btn_collectors:"TO COLLECTORS,", btn_artists:"TO ARTISTS,",

    collectors_title:"To Collectors,", collectors_lede:"Art selected with intention.",
    collectors_p1:"We're currently working selectively with artists and sourcing works for private clients and creative environments, focused on discovering, sourcing and placing exceptional works within private collections, creative environments and luxury spaces.",
    collectors_p2:"We work selectively with a developing roster of artists whose practices we believe possess a distinctive point of view, cultural relevance and lasting character.",
    collectors_p3:"For collectors seeking a particular artist, work or direction, our team can source and present works privately according to your interests, aesthetic and environment.",
    collectors_p4:"Our artist roster and available works are shared privately and by enquiry.",
    collectors_cta:"If you would like to receive our current selection or discuss a private sourcing request, please contact our team.",
    collectors_link:"PRIVATE COLLECTOR ENQUIRIES",

    artists_title:"To Artists,", artists_lede:"Selective relationships, thoughtful placements.",
    artists_p1:"We are interested in artists with a distinctive visual language, considered practice and a strong individual point of view.",
    artists_p2:"Our approach is intentionally selective. We build relationships with artists whose work we believe can create meaningful connections with the right collectors, spaces and cultural environments.",
    artists_p3:"If you are an artist or represent an artist whose practice you believe may align with Yvis Hausen, we invite you to introduce your work to our team.",
    artists_p4:"Please include your portfolio, website or Instagram, a short biography, current representation (if applicable), and any relevant information regarding available works.",
    artists_p5:"All submissions are reviewed privately.",
    artists_link:"ARTIST SUBMISSIONS",

    enquiry_heading:"Interested in working together?",
    enquiry_text:"For project enquiries, collaborations or further information, please get in touch with our team.",
    enquiry_link:"GET IN TOUCH"
  },
  fr: {
    enquire_btn:"CONTACT",
    lang_label:"LANGUE", lang_option_en:"Anglais", lang_option_fr:"Français", lang_option_it:"Italien",
    group_creative:"MAISON CRÉATIVE", group_curation:"CURATION", group_art:"ART & CULTURE",
    cat_sound_label:"ARCHITECTURE SONORE", cat_sound_desc:"Compositions originales — musiques de défilé, identités sonores, musiques de film, paysages sonores immersifs",
    cat_visual_label:"DIRECTION VISUELLE", cat_visual_desc:"Design visuel sur mesure pour la mode, les événements et les marques — invitations, édition & impression, design de menus, magazines & publications",
    cat_sceno_label:"SCÉNOGRAPHIE", cat_sceno_desc:"Univers spatiaux, décors et environnements conçus pour la mode, le cinéma, les expositions et les expériences culturelles",
    cat_talent_label:"PORTFOLIOS DE TALENTS", cat_talent_desc:"Casting de talents pour la mode et le cinéma.",
    cat_event_label:"CURATION D'ÉVÉNEMENTS", cat_event_desc:"Environnements, rassemblements et expériences sur mesure pour marques, institutions et clients privés",
    cat_exhib_label:"EXPOSITIONS", cat_exhib_desc:"Commissariat et présentation d'expositions pour institutions, galeries et collections privées",
    cat_art_label:"ART PRIVÉ", cat_art_desc:"Conseil en art privé & sourcing — recherche, sourcing, curation et accompagnement à l'acquisition pour collections privées",
    footer_line:"YVIS HAUSEN  —  PRATIQUE PRIVÉE  —  SUR DEMANDE UNIQUEMENT",

    tile_ops_title:"OPÉRATIONS", tile_mkt_link:"MARKETING",
    tile_mkt_desc:"Publicités Meta, gouvernance de marque, promotion.",
    tile_talent_title:"REPRÉSENTATION DE TALENTS", tile_talent_link1:"TALENTS",
    tile_talent_link1_desc:"Casting de talents pour la mode et le cinéma.", tile_talent_link2:"AGENTS",
    tile_talent_link2_desc:"Représentation, placement et gestion de carrière dans la mode et le cinéma.",
    tile_creative_title:"MAISON CRÉATIVE",
    tile_art_title:"ART & CULTURE",

    db_heading_title:"BASE DE DONNÉES YVIS HAUSEN", db_heading_sub:"SYSTÈME DE CLASSEMENT DE PROJETS",
    code_label:"CODE PRIVÉ", code_cancel:"ANNULER", code_error:"ACCÈS REFUSÉ", code_restricted:"ACCÈS RESTREINT. LES CODES D'ACCÈS SONT FOURNIS UNIQUEMENT PAR DES AGENTS AUTORISÉS",
    db_eyebrow:"BASE DE PROJETS : PORTFOLIO", db_404:"ERREUR 404",

    page_sound_title:"Architecture Sonore", page_sound_lede:"La composition comme langage spatial et sensoriel.",
    page_sound_p1:"Yvis Hausen crée des sons originaux pour la mode, le cinéma et les environnements immersifs — un travail conçu pour être ressenti autant qu'entendu, façonnant l'ambiance, le rythme et la mémoire d'un lieu ou d'un récit.",
    page_sound_p2:"Nos compositions sont développées spécifiquement pour le défilé, l'écran et l'installation, traduisant l'identité d'une marque ou la vision d'un réalisateur en forme sonore.",
    page_sound_p3:"Le travail actuel est mené de façon privée et sur commande, en étroite collaboration avec les équipes créatives de chaque projet.",

    page_visual_title:"Direction Visuelle", page_visual_lede:"Un design réfléchi entre mode, marque et impression.",
    page_visual_p1:"Nous créons des travaux visuels sur mesure pour des maisons de mode, des événements et des institutions — des invitations aux mises en page éditoriales, jusqu'au design de menus et de publications.",
    page_visual_p2:"Chaque commande est traitée comme un projet de design à part entière, construit à partir du langage de la marque ou de l'occasion qu'elle sert, plutôt que d'un style de maison figé.",
    page_visual_p3:"Nos travaux récents incluent un design de menu épuré et minimal — traitant la page imprimée avec la même précision qu'une invitation de défilé.",

    page_sceno_title:"Scénographie", page_sceno_lede:"Des univers spatiaux pour la mode, le cinéma et l'exposition.",
    page_sceno_p1:"Yvis Hausen conçoit des décors et des environnements pour les présentations de mode, la production cinématographique, les expositions et les expériences culturelles — des espaces construits pour porter un récit.",
    page_sceno_p2:"Notre approche traite la scénographie comme une narration en trois dimensions, façonnant la manière dont un public se déplace et vit un moment.",
    page_sceno_p3:"Le travail est développé de façon privée, en collaboration avec des réalisateurs, des commissaires et des équipes de marque.",

    page_talent_title:"Représentation de Talents", page_talent_lede:"Casting de talents pour la mode et le cinéma.",
    page_talent_p1:"Nous identifions, représentons et plaçons des talents dans la mode et le cinéma, en étroite collaboration avec les directeurs de casting, les marques et les équipes de production.",
    page_talent_p2:"Notre portefeuille est développé de façon sélective, avec une attention particulière à la présence, la polyvalence et un point de vue distinctif.",
    page_talent_p3:"Les demandes de représentation ou de casting sont traitées de façon privée.",

    page_event_title:"Curation d'Événements", page_event_lede:"Des rassemblements sur mesure, pensés du premier concept au moindre détail.",
    page_event_p1:"Yvis Hausen conçoit des environnements, des rassemblements et des expériences pour des marques, des institutions et des clients privés — des occasions construites autour d'une idée claire plutôt que d'un modèle.",
    page_event_p2:"Nous intervenons sur le concept, le design spatial, l'expérience des invités et l'atmosphère, en façonnant chaque détail vers un résultat unique et réfléchi.",
    page_event_p3:"Le travail actuel est mené de façon privée et sur introduction.",

    page_exhib_title:"Expositions", page_exhib_lede:"Des présentations culturelles, façonnées avec intention.",
    page_exhib_p1:"Nous développons et organisons des expositions pour des institutions culturelles, des galeries et des collections privées — traduisant un corpus d'œuvres ou une idée en une expérience spatiale réfléchie.",
    page_exhib_p2:"Notre approche couvre le concept, la mise en espace et la présentation, en étroite collaboration avec les artistes, les commissaires et les institutions pour façonner la manière dont l'œuvre est rencontrée.",
    page_exhib_p3:"Les demandes concernant le commissariat d'exposition sont accueillies de façon privée.",

    page_art_title:"Conseil Art & Culture",
    page_art_p1:"Yvis Hausen développe une pratique de conseil en art privé, centrée sur la découverte, le sourcing et le placement d'œuvres exceptionnelles dans l'art contemporain et la culture visuelle.",
    page_art_p2:"Alors que nos autres activités au sein du secteur Creative House croisaient de plus en plus artistes, collectionneurs, designers et institutions culturelles, nous avons développé une pratique dédiée de Conseil Art & Culture. Notre approche est délibérément sélective, mettant en relation artistes, collectionneurs, institutions créatives et environnements de luxe par des introductions réfléchies et un sourcing sur mesure.",
    page_art_p3:"Nous développons actuellement des relations avec des artistes, des galeries, des collectionneurs et des clients privés, en amont du lancement formel de la pratique.",
    btn_collectors:"AUX COLLECTIONNEURS,", btn_artists:"AUX ARTISTES,",

    collectors_title:"Aux Collectionneurs,", collectors_lede:"L'art choisi avec intention.",
    collectors_p1:"Nous travaillons actuellement de façon sélective avec des artistes et sourçons des œuvres pour des clients privés et des environnements créatifs, en nous concentrant sur la découverte, le sourcing et le placement d'œuvres exceptionnelles au sein de collections privées, d'environnements créatifs et d'espaces de luxe.",
    collectors_p2:"Nous travaillons de façon sélective avec un portefeuille d'artistes en développement, dont nous estimons que les pratiques possèdent un point de vue distinctif, une pertinence culturelle et un caractère durable.",
    collectors_p3:"Pour les collectionneurs recherchant un artiste, une œuvre ou une direction particulière, notre équipe peut sourcer et présenter des œuvres de façon privée, selon vos intérêts, votre esthétique et votre environnement.",
    collectors_p4:"Notre portefeuille d'artistes et les œuvres disponibles sont partagés de façon privée et sur demande.",
    collectors_cta:"Si vous souhaitez recevoir notre sélection actuelle ou discuter d'une demande de sourcing privée, veuillez contacter notre équipe.",
    collectors_link:"DEMANDES COLLECTIONNEURS PRIVÉS",

    artists_title:"Aux Artistes,", artists_lede:"Des relations sélectives, des placements réfléchis.",
    artists_p1:"Nous nous intéressons aux artistes dotés d'un langage visuel distinctif, d'une pratique réfléchie et d'un point de vue individuel fort.",
    artists_p2:"Notre approche est délibérément sélective. Nous construisons des relations avec des artistes dont nous pensons que le travail peut créer des connexions significatives avec les bons collectionneurs, les bons espaces et les bons environnements culturels.",
    artists_p3:"Si vous êtes artiste ou représentez un artiste dont la pratique vous semble pouvoir s'aligner avec Yvis Hausen, nous vous invitons à présenter son travail à notre équipe.",
    artists_p4:"Merci d'inclure un portfolio, un site web ou un compte Instagram, une courte biographie, une représentation actuelle (le cas échéant), et toute information pertinente concernant les œuvres disponibles.",
    artists_p5:"Toutes les candidatures sont examinées de façon privée.",
    artists_link:"CANDIDATURES ARTISTES",

    enquiry_heading:"Envie de collaborer ?",
    enquiry_text:"Pour toute demande de projet, collaboration ou information complémentaire, veuillez contacter notre équipe.",
    enquiry_link:"NOUS CONTACTER"
  },
  it: {
    enquire_btn:"CONTATTI",
    lang_label:"LINGUA", lang_option_en:"Inglese", lang_option_fr:"Francese", lang_option_it:"Italiano",
    group_creative:"CASA CREATIVA", group_curation:"CURATELA", group_art:"ARTE & CULTURA",
    cat_sound_label:"ARCHITETTURA DEL SUONO", cat_sound_desc:"Composizioni originali — colonne sonore per sfilate, identità sonore, colonne sonore cinematografiche, paesaggi sonori immersivi",
    cat_visual_label:"DIREZIONE VISIVA", cat_visual_desc:"Design visivo su misura per moda, eventi e brand — inviti, editoria & stampa, design di menu, riviste & pubblicazioni",
    cat_sceno_label:"SCENOGRAFIA", cat_sceno_desc:"Mondi spaziali, scenografie e ambienti creati per moda, cinema, mostre ed esperienze culturali",
    cat_talent_label:"PORTFOLIO TALENTI", cat_talent_desc:"Casting di talenti per moda e cinema.",
    cat_event_label:"CURATELA EVENTI", cat_event_desc:"Ambienti, incontri ed esperienze su misura per brand, istituzioni e clienti privati",
    cat_exhib_label:"MOSTRE", cat_exhib_desc:"Curatela e presentazione di mostre per istituzioni, gallerie e collezioni private",
    cat_art_label:"ARTE PRIVATA", cat_art_desc:"Consulenza artistica privata & sourcing — ricerca, sourcing, curatela e supporto all'acquisizione per collezioni private",
    footer_line:"YVIS HAUSEN  —  STUDIO PRIVATO  —  SOLO SU RICHIESTA",

    tile_ops_title:"OPERAZIONI", tile_mkt_link:"MARKETING",
    tile_mkt_desc:"Meta Ads, governance del brand, promozione.",
    tile_talent_title:"RAPPRESENTANZA TALENTI", tile_talent_link1:"TALENTI",
    tile_talent_link1_desc:"Casting di talenti per moda e cinema.", tile_talent_link2:"AGENTI",
    tile_talent_link2_desc:"Rappresentanza, collocamento e gestione della carriera in moda e cinema.",
    tile_creative_title:"CASA CREATIVA",
    tile_art_title:"ARTE & CULTURA",

    db_heading_title:"DATABASE YVIS HAUSEN", db_heading_sub:"SISTEMA DI ARCHIVIAZIONE PROGETTI",
    code_label:"CODICE PRIVATO", code_cancel:"ANNULLA", code_error:"ACCESSO NEGATO", code_restricted:"ACCESSO LIMITATO. I CODICI DI ACCESSO SONO FORNITI SOLO DA AGENTI AUTORIZZATI",
    db_eyebrow:"DATABASE PROGETTI: PORTFOLIO", db_404:"ERRORE 404",

    page_sound_title:"Architettura del Suono", page_sound_lede:"La composizione come linguaggio spaziale e sensoriale.",
    page_sound_p1:"Yvis Hausen crea suoni originali per moda, cinema e ambienti immersivi — un lavoro pensato per essere percepito tanto quanto ascoltato, capace di plasmare atmosfera, ritmo e memoria di uno spazio o di una storia.",
    page_sound_p2:"Le nostre composizioni sono sviluppate appositamente per passerella, schermo e installazione, traducendo l'identità di un brand o la visione di un regista in forma sonora.",
    page_sound_p3:"Il lavoro attuale è svolto in forma privata e su commissione, in stretta collaborazione con i team creativi di ciascun progetto.",

    page_visual_title:"Direzione Visiva", page_visual_lede:"Un design ponderato tra moda, brand e stampa.",
    page_visual_p1:"Creiamo lavori visivi su misura per case di moda, eventi e istituzioni — dagli inviti agli eventi alle impaginazioni editoriali, fino al design di menu e pubblicazioni.",
    page_visual_p2:"Ogni incarico è trattato come un progetto di design a sé stante, costruito a partire dal linguaggio del brand o dell'occasione che serve, piuttosto che da uno stile fisso.",
    page_visual_p3:"Il lavoro recente include un design di menu raffinato e minimale — trattando la pagina stampata con la stessa precisione di un invito di passerella.",

    page_sceno_title:"Scenografia", page_sceno_lede:"Mondi spaziali per moda, cinema ed esposizione.",
    page_sceno_p1:"Yvis Hausen progetta scenografie e ambienti per presentazioni di moda, produzioni cinematografiche, mostre ed esperienze culturali — spazi costruiti per veicolare una narrazione.",
    page_sceno_p2:"Il nostro approccio tratta la scenografia come narrazione in tre dimensioni, definendo il modo in cui il pubblico si muove e vive un momento.",
    page_sceno_p3:"Il lavoro viene sviluppato in forma privata, in collaborazione con registi, curatori e team di brand.",

    page_talent_title:"Rappresentanza Talenti", page_talent_lede:"Casting di talenti per moda e cinema.",
    page_talent_p1:"Individuiamo, rappresentiamo e collochiamo talenti nel mondo della moda e del cinema, lavorando a stretto contatto con direttori di casting, brand e team di produzione.",
    page_talent_p2:"Il nostro roster viene sviluppato in modo selettivo, con particolare attenzione a presenza, versatilità e un punto di vista distintivo.",
    page_talent_p3:"Le richieste di rappresentanza o casting vengono gestite in forma privata.",

    page_event_title:"Curatela Eventi", page_event_lede:"Incontri su misura, curati dalla prima idea al minimo dettaglio.",
    page_event_p1:"Yvis Hausen cura ambienti, incontri ed esperienze per brand, istituzioni e clienti privati — occasioni costruite attorno a un'idea chiara piuttosto che a un modello prestabilito.",
    page_event_p2:"Lavoriamo su concept, design spaziale, esperienza degli ospiti e atmosfera, definendo ogni dettaglio verso un unico risultato ponderato.",
    page_event_p3:"Il lavoro attuale è svolto in forma privata e su presentazione.",

    page_exhib_title:"Mostre", page_exhib_lede:"Presentazioni culturali, plasmate con intenzione.",
    page_exhib_p1:"Sviluppiamo e curiamo mostre per istituzioni culturali, gallerie e collezioni private — traducendo un corpus di opere o un'idea in un'esperienza spaziale ponderata.",
    page_exhib_p2:"Il nostro approccio spazia da concept, allestimento e presentazione, lavorando a stretto contatto con artisti, curatori e istituzioni per definire il modo in cui l'opera viene incontrata.",
    page_exhib_p3:"Le richieste relative alla curatela di mostre sono benvenute in forma privata.",

    page_art_title:"Consulenza Arte & Cultura",
    page_art_p1:"Yvis Hausen sta sviluppando una pratica di consulenza artistica privata incentrata sulla scoperta, il sourcing e il collocamento di opere eccezionali nell'ambito dell'arte contemporanea e della cultura visiva.",
    page_art_p2:"Poiché il nostro altro lavoro nel settore Creative House si intrecciava sempre più con artisti, collezionisti, designer e istituzioni culturali, abbiamo sviluppato una pratica dedicata di Consulenza Arte & Cultura. Il nostro approccio è volutamente selettivo, mettendo in relazione artisti, collezionisti, istituzioni creative e ambienti di lusso attraverso presentazioni ponderate e sourcing su misura.",
    page_art_p3:"Stiamo attualmente sviluppando relazioni con artisti, gallerie, collezionisti e clienti privati in vista del lancio formale della pratica.",
    btn_collectors:"AI COLLEZIONISTI,", btn_artists:"AGLI ARTISTI,",

    collectors_title:"Ai Collezionisti,", collectors_lede:"Arte scelta con intenzione.",
    collectors_p1:"Al momento lavoriamo in modo selettivo con artisti e ricerchiamo opere per clienti privati e ambienti creativi, concentrandoci sulla scoperta, il sourcing e il collocamento di opere eccezionali all'interno di collezioni private, ambienti creativi e spazi di lusso.",
    collectors_p2:"Lavoriamo in modo selettivo con un roster di artisti in sviluppo, le cui pratiche riteniamo possiedano un punto di vista distintivo, rilevanza culturale e carattere duraturo.",
    collectors_p3:"Per i collezionisti alla ricerca di un artista, un'opera o una direzione particolare, il nostro team può ricercare e presentare opere in forma privata, in base ai vostri interessi, alla vostra estetica e al vostro ambiente.",
    collectors_p4:"Il nostro roster di artisti e le opere disponibili vengono condivisi in forma privata e su richiesta.",
    collectors_cta:"Se desiderate ricevere la nostra selezione attuale o discutere una richiesta di sourcing privata, vi preghiamo di contattare il nostro team.",
    collectors_link:"RICHIESTE COLLEZIONISTI PRIVATI",

    artists_title:"Agli Artisti,", artists_lede:"Relazioni selettive, collocamenti ponderati.",
    artists_p1:"Siamo interessati ad artisti con un linguaggio visivo distintivo, una pratica ponderata e un forte punto di vista individuale.",
    artists_p2:"Il nostro approccio è volutamente selettivo. Costruiamo relazioni con artisti la cui opera riteniamo possa creare connessioni significative con i giusti collezionisti, spazi e ambienti culturali.",
    artists_p3:"Se siete artisti o rappresentate un artista la cui pratica ritenete possa allinearsi con Yvis Hausen, vi invitiamo a presentare il vostro lavoro al nostro team.",
    artists_p4:"Vi preghiamo di includere portfolio, sito web o Instagram, una breve biografia, la rappresentanza attuale (se presente) e ogni informazione rilevante riguardo alle opere disponibili.",
    artists_p5:"Tutte le candidature vengono esaminate in forma privata.",
    artists_link:"CANDIDATURE ARTISTI",

    enquiry_heading:"Interessati a collaborare?",
    enquiry_text:"Per richieste di progetto, collaborazioni o ulteriori informazioni, vi preghiamo di contattare il nostro team.",
    enquiry_link:"CONTATTACI"
  }
};

let currentLang = 'en';
let phraseIndex = 0;

function applyLanguage(lang){
  currentLang = lang;
  document.documentElement.setAttribute('lang', lang);
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if(I18N[lang][key] !== undefined) el.textContent = I18N[lang][key];
  });
  document.querySelectorAll('.lang-option').forEach(o => o.classList.toggle('active', o.getAttribute('data-lang') === lang));
  const subtitleEl = document.getElementById('subtitle');
  if(subtitleEl){
    phraseIndex = 0;
    subtitleEl.textContent = SUBTITLES[lang][0];
  }
}

document.querySelectorAll('.lang-option').forEach(opt => {
  opt.addEventListener('click', (e) => {
    e.stopPropagation();
    applyLanguage(opt.getAttribute('data-lang'));
    const dropdown = opt.closest('.lang-dropdown');
    if(dropdown) dropdown.classList.remove('open');
  });
});

const langToggle = document.querySelector('.lang-toggle');
if(langToggle){
  langToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    langToggle.closest('.lang-dropdown').classList.toggle('open');
  });
  document.addEventListener('click', () => {
    document.querySelectorAll('.lang-dropdown.open').forEach(d => d.classList.remove('open'));
  });
}

// ---------- Cycling subtitle ----------
const subtitleEl = document.getElementById('subtitle');
if(subtitleEl){
  setInterval(() => {
    subtitleEl.classList.add('swipe');
    setTimeout(() => {
      const arr = SUBTITLES[currentLang];
      phraseIndex = (phraseIndex + 1) % arr.length;
      subtitleEl.textContent = arr[phraseIndex];
      subtitleEl.classList.remove('swipe');
    }, 700);
  }, 3400);
}

// ---------- Filing cabinet: private-code gate ----------
// Each folder's access code lives here — currently all "0000", but every
// folder already has its own entry, so assigning a folder a unique code
// later is a one-line change, not a restructure.
const FOLDER_CODES = {
  'sound':'0000',
  'visual-direction':'0000',
  'scenography':'0000',
  'talent-representation':'0000',
  'event-curation':'0000',
  'exhibitions':'0000',
  'private-art':'0000'
};

let pendingFolder = null;
const codeModal = document.getElementById('codeModal');
const codeInput = document.getElementById('codeInput');
const codeError = document.getElementById('codeError');
const codeCancel = document.getElementById('codeCancel');
const codeRestricted = document.getElementById('codeRestricted');
let failedAttempts = 0;   // after two wrong codes, explain how access works

function openCodeModal(folderKey){
  pendingFolder = folderKey;
  if(!codeModal) return;
  codeError.classList.remove('show');
  if(codeRestricted) codeRestricted.classList.toggle('show', failedAttempts >= 2);
  codeInput.value = '';
  codeModal.classList.add('open');
  setTimeout(() => codeInput.focus(), 50);
}

function closeCodeModal(){
  if(!codeModal) return;
  codeModal.classList.remove('open');
  pendingFolder = null;
}

function goToDatabase(folderKey){
  // Single-file preview build has #route-database-<key> sections and uses hash routing.
  // The real multi-page site instead has a standalone database-<key>.html file.
  if(document.getElementById('route-database-' + folderKey)){
    window.location.hash = 'database-' + folderKey;
  }else{
    window.location.href = 'database-' + folderKey + '.html';
  }
}

function submitCode(){
  if(!pendingFolder) return;
  const expected = FOLDER_CODES[pendingFolder];
  if(expected !== undefined && codeInput.value === expected){
    const folderKey = pendingFolder;
    closeCodeModal();
    goToDatabase(folderKey);
  }else{
    failedAttempts++;
    codeError.classList.add('show');
    if(codeRestricted && failedAttempts >= 2) codeRestricted.classList.add('show');
    codeInput.value = '';
  }
}

document.querySelectorAll('.folder').forEach(f => {
  f.addEventListener('click', () => openCodeModal(f.getAttribute('data-folder')));
});

if(codeCancel){ codeCancel.addEventListener('click', closeCodeModal); }
if(codeInput){
  codeInput.addEventListener('keydown', (e) => { if(e.key === 'Enter') submitCode(); });
  codeInput.addEventListener('input', () => {
    const expected = pendingFolder ? FOLDER_CODES[pendingFolder] : null;
    if(expected && codeInput.value.length === expected.length) submitCode();
  });
}
if(codeModal){
  codeModal.addEventListener('click', (e) => { if(e.target === codeModal) closeCodeModal(); });
}

// ---------- Filing cabinet: papers riffle as the cursor moves along a file ----------
// Each sheet eases towards a target on every frame (a soft spring), so the
// motion stays fluid however fast the cursor moves. Sheets in the file under
// the cursor lift in a wave that follows the pointer; the neighbouring files
// stir slightly; everything drifts back when the cursor leaves. The metal
// sheen on the casing slides a little with the cursor too.
(function(){
  const cabinet = document.querySelector('.filing-cabinet');
  if(!cabinet || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const folders = Array.from(cabinet.querySelectorAll('.folder')).map(el => ({
    el, body: el.querySelector('.folder-body'),
    papers: Array.from(el.querySelectorAll('.paper')).map((p, i) => ({ el: p, n: i + 1, y: 0, r: 0, x: 0, vy: 0, vr: 0, vx: 0 }))
  }));
  let pointer = null, raf = 0;
  function targetFor(f, fi, p){
    if(!pointer) return [0, 0, 0];
    const d = Math.abs(fi - pointer.fi);
    if(d > 1) return [0, 0, 0];
    const r = f.el.getBoundingClientRect();
    const x = Math.min(Math.max((pointer.x - r.left) / r.width, 0), 1);
    const k = d === 0 ? 1 : 0.3;
    // back sheets rise a little more, with a gentle wave travelling across
    const wave = 0.75 + 0.25 * Math.sin(x * Math.PI * 2 + p.n * 0.9);
    return [-(1.5 + p.n * 1.2) * wave * k, (0.5 - x) * 0.35 * k, (x - 0.5) * 6 * k];
  }
  function step(){
    let moving = false;
    folders.forEach((f, fi) => {
      f.papers.forEach(p => {
        const [ty, tr, tx] = targetFor(f, fi, p);
        // critically-damped-ish spring; later sheets respond a touch later
        const stiff = 0.075 - p.n * 0.006, damp = 0.78;
        p.vy = (p.vy + (ty - p.y) * stiff) * damp; p.y += p.vy;
        p.vr = (p.vr + (tr - p.r) * stiff) * damp; p.r += p.vr;
        p.vx = (p.vx + (tx - p.x) * stiff) * damp; p.x += p.vx;
        if(Math.abs(ty - p.y) + Math.abs(p.vy) + Math.abs(tr - p.r) * 10 + Math.abs(tx - p.x) > 0.02) moving = true;
        p.el.style.transform = 'translate3d(' + p.x.toFixed(2) + 'px,' + p.y.toFixed(2) + 'px,0) rotate(' + p.r.toFixed(3) + 'deg)';
      });
    });
    raf = moving ? requestAnimationFrame(step) : 0;
  }
  function kick(){ if(!raf) raf = requestAnimationFrame(step); }
  cabinet.addEventListener('mousemove', e => {
    const el = e.target.closest('.folder');
    const fi = folders.findIndex(f => f.el === el);
    pointer = fi < 0 ? null : { x: e.clientX, fi };
    if(fi >= 0){
      const f = folders[fi], r = f.el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width;
      f.body.style.setProperty('--sheen', (30 + x * 40).toFixed(1) + '%');
      f.body.style.setProperty('--sheen2', (80 - x * 30).toFixed(1) + '%');
    }
    kick();
  });
  cabinet.addEventListener('mouseleave', () => {
    pointer = null;
    folders.forEach(f => { f.body.style.removeProperty('--sheen'); f.body.style.removeProperty('--sheen2'); });
    kick();
  });
})();
