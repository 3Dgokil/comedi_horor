import os, json, random, requests, re
import streamlit as st

st.set_page_config(page_title="Gokil 3D Shorts Studio", page_icon="🤣", layout="wide")
st.title("🤣 Gokil 3D — Shorts Studio")
st.caption("DILIHAT → BERTAHAN → KEMBALI → SUBSCRIBE | Generator komedi animasi 3D")

LANGUAGES = ["Bahasa Indonesia", "English", "Português do Brasil", "Español", "हिन्दी (Hindi)", "日本語 (Japanese)", "Bahasa Melayu", "Bahasa lain (isi sendiri)"]

# Local ideas are deliberately distinct, including different CTA punchlines.
LOCAL_IDEAS = [
 {"title":"DOMPET TIPIS, GAYA SULTAN! 😂💸","hook":"Karakter 3D bergaya sultan membuka dompet dengan dramatis—yang keluar cuma debu dan satu struk panjang.","story":"Bimo pamer seolah paling kaya di tongkrongan. Saat teman-temannya meminta traktiran, ia membuka dompet kosong dengan gaya pesulap.","dialogue":[{"time":"00:00–00:02","speaker":"BIMO","line":"Tenang! Malam ini gue traktir semuanya!"},{"time":"00:02–00:05","speaker":"TEMAN","line":"Wih, sultan baru turun gunung!"},{"time":"00:05–00:08","speaker":"BIMO","line":"Dompet gue memang tipis… tapi penuh kenangan."},{"time":"00:08–00:10","speaker":"TEMAN","line":"Kalau ikut ketawa, traktir kami pakai subscribe aja!"}],"punchline":"Dompet Bimo hanya berisi struk belanja dan kartu member kedaluwarsa.","ending":"Semua tertawa; Bimo menutup dompet dengan gaya pahlawan.","cta_note":"CTA menjadi lelucon tentang traktiran, bukan kalimat ajakan generik."},
 {"title":"GARA-GARA MIE INSTAN! 🍜🤣","hook":"Mangkuk mie raksasa jatuh dari langit tepat di depan karakter 3D yang kelaparan.","story":"Ucup mengaku ahli memasak. Ia memasukkan mie, bumbu, es batu, dan saus cokelat ke panci. Temannya mencicipi lalu langsung berubah pucat.","dialogue":[{"time":"00:00–00:02","speaker":"UCUP","line":"Hari ini gue masak menu bintang lima!"},{"time":"00:02–00:05","speaker":"TEMAN","line":"Kenapa ada es batu sama cokelat?!"},{"time":"00:05–00:08","speaker":"UCUP","line":"Ini namanya fusion cuisine!"},{"time":"00:08–00:10","speaker":"TEMAN","line":"Fusion apaan? Subscribe dulu biar chef ini pensiun!"}],"punchline":"Mie itu bergerak sendiri dan kabur dari panci.","ending":"Ucup mengejar mie dengan sendok, sementara temannya menahan tawa.","cta_note":"CTA terkait langsung dengan lelucon masakan gagal."},
 {"title":"ROBOTNYA MALAH NGUTANG! 🤖💳","hook":"Robot 3D membuka dadanya seperti mesin canggih, tetapi yang muncul adalah notifikasi tagihan.","story":"Doni membeli robot pintar untuk mengatur keuangan. Robot itu memindai rekening Doni lalu mengaktifkan mode darurat karena saldo hampir nol.","dialogue":[{"time":"00:00–00:02","speaker":"DONI","line":"Robot, bikin gue kaya dalam semalam!"},{"time":"00:02–00:05","speaker":"ROBOT","line":"Memindai saldo… turut berduka."},{"time":"00:05–00:08","speaker":"DONI","line":"Lah, lu robot apa debt collector?!"},{"time":"00:08–00:10","speaker":"ROBOT","line":"Bantu upgrade hidup saya: subscribe dulu, cicilan belakangan!"}],"punchline":"Robot mengeluarkan helm penagih utang dan mengetuk pintu sendiri.","ending":"Doni dan robot kabur berlawanan arah.","cta_note":"CTA memakai tema robot dan cicilan, berbeda dari ide lain."},
 {"title":"KUCING JADI BOS! 🐱👔","hook":"Seekor kucing 3D melompat ke meja rapat dan semua manusia langsung berdiri hormat.","story":"Karyawan panik karena bos baru ternyata seekor kucing yang cuma ingin tidur di atas laptop. Setiap kali ada yang protes, kucing menekan tombol rapat.","dialogue":[{"time":"00:00–00:02","speaker":"KARYAWAN","line":"Katanya bos baru jenius!"},{"time":"00:02–00:05","speaker":"KARYAWAN 2","line":"Dia baru saja tidur di atas laporan kita!"},{"time":"00:05–00:08","speaker":"KUCING","line":"Meong. Rapat selesai."},{"time":"00:08–00:10","speaker":"KARYAWAN","line":"Bosnya tidur, kita yang lembur. Subscribe biar kita bisa resign!"}],"punchline":"Kucing menekan tombol keluar rapat dan mendapat bonus ikan.","ending":"Para karyawan menatap kamera dengan wajah pasrah.","cta_note":"CTA terkait dunia kerja dan bos kucing."},
 {"title":"PENDEKAR SALAH JURUS! 🥋💨","hook":"Pendekar 3D mengambil kuda-kuda epik, lalu terpeleset kulit pisang sebelum bertarung.","story":"Pendekar sombong menantang lawan dengan jurus rahasia. Ia berteriak keras, tetapi jurusnya malah membuat celananya berkibar seperti bendera.","dialogue":[{"time":"00:00–00:02","speaker":"PENDEKAR","line":"Rasakan jurus naga seribu badai!"},{"time":"00:02–00:05","speaker":"LAWAN","line":"Kok cuma angin lewat?"},{"time":"00:05–00:08","speaker":"PENDEKAR","line":"Itu pemanasan tingkat dewa!"},{"time":"00:08–00:10","speaker":"LAWAN","line":"Kalau jurusnya bikin ngakak, subscribe dulu sebelum dia latihan lagi!"}],"punchline":"Angin dari jurusnya menerbangkan topi pendekar sendiri.","ending":"Pendekar mengejar topi sambil tetap berpose serius.","cta_note":"CTA sesuai lelucon jurus gagal."},
]

def get_key():
    try:
        k = st.secrets.get("GEMINI_API_KEY", "")
        if k: return k
    except Exception: pass
    return os.getenv("GEMINI_API_KEY", "")

def gemini_generate(key, model, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    resp = requests.post(url, headers={"x-goog-api-key": key, "Content-Type":"application/json"},
        json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":1.0,"responseMimeType":"application/json"}}, timeout=90)
    if not resp.ok:
        try: message = resp.json().get("error",{}).get("message", resp.text)
        except Exception: message = resp.text
        raise RuntimeError(f"Gemini API {resp.status_code}: {message}")
    body = resp.json()
    text = body["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)

def ensure_cta(idea, language):
    # Never replace an existing CTA; only add a tailored fallback if none exists.
    ds = idea.get("dialogue") or []
    joined = " ".join(str(d.get("line", "")) for d in ds).lower()
    keywords = ["subscribe", "subscribed", "langgan", "subscribe dulu", "follow", "ikuti"]
    has_cta = any(k in joined for k in keywords)
    if not has_cta:
        if language == "English": line = "If that made you laugh, hit subscribe before this gets even weirder!"
        elif language == "Português do Brasil": line = "Se você riu, se inscreve antes que isso fique ainda mais maluco!"
        elif language == "Español": line = "Si te hizo reír, suscríbete antes de que esto se ponga más loco!"
        elif language == "Bahasa Melayu": line = "Kalau ini buat kau ketawa, langgan dulu sebelum jadi makin pelik!"
        else: line = random.choice([
            "Kalau lu ketawa, bayar pakai subscribe aja—gratis, gak perlu transfer!",
            "Subscribe dulu, biar nasib gue gak selucu dompet gue!",
            "Kalau ngakak, pencet subscribe sebelum masalah baru datang!",
            "Bantu karakter ini naik level—subscribe, bukan kasih utang!",
            "Subscribe dulu! Tenang, gak ada biaya admin kayak transfer!"
        ])
        ds.append({"time":"AKHIR","speaker":"KARAKTER","line":line})
        idea["dialogue"] = ds
        idea["cta_note"] = "CTA cadangan ditambahkan dan disesuaikan dengan bahasa yang dipilih."
    return idea

def build_prompts(idea, style, duration, language, aspect, character):
    dialogue = "\n".join(f'{d.get("time", "")} | {d.get("speaker", "")}: "{d.get("line", "")}"' for d in idea.get("dialogue", []))
    character_guide = {
        "Semar": "Use Semar as the recognizable lead: a friendly Javanese wayang-inspired 3D character, round belly, distinctive traditional Javanese attire and blangkon, warm expressive face. Treat respectfully and consistently.",
        "Skeleton": "Use a funny stylized 3D skeleton as the lead: clean ivory bones, oversized expressive eye sockets with readable cartoon emotion, flexible comedic body language, no gore or horror violence.",
        "Manusia 3D": "Use original human 3D characters with expressive faces, clear emotions, believable hands and body proportions, distinctive clothing, and consistent appearance across every shot.",
        "Semar + Skeleton": "Use both a recognizable Semar-inspired Javanese wayang 3D character and a funny ivory 3D skeleton as co-leads. Keep their designs, clothing, proportions, and personalities consistent across every shot.",
        "Skeleton + Manusia": "Use a funny stylized ivory 3D skeleton and one original human 3D character as co-leads. Keep designs consistent across shots; no gore.",
        "Acak sesuai cerita": "Choose the most suitable combination of original human 3D characters, Semar-inspired character, and/or funny skeleton for this specific joke. Keep every chosen character visually consistent across shots."
    }
    character_guide_text = character_guide.get(character, character_guide["Acak sesuai cerita"])
    idea["flow_prompt"] = f"""Create a {duration} vertical {aspect} YouTube Shorts video for Gokil 3D.
CHARACTER MODE: {character}
CHARACTER DESIGN — follow exactly: {character_guide_text}
VISUAL STYLE: high-quality stylized 3D animated comedy, expressive faces, appealing character design, detailed materials, cinematic lighting, clean readable action, smooth motion, exaggerated but believable cartoon body language.
GOAL: entertain viewers and gain subscribers through an original joke.
TITLE: {idea.get('title','')}
HOOK (start immediately, first 0–2 seconds): {idea.get('hook','')}
STORY: {idea.get('story','')}
DIALOGUE — follow exactly; do not omit, rewrite, reorder, or add any dialogue:
{dialogue}
PUNCHLINE: {idea.get('punchline','')}
ENDING: {idea.get('ending','')}
IMPORTANT: preserve the CTA line exactly as written in the dialogue and make it feel like part of the joke. Spoken language: {language}. Natural pronunciation and accurate lip sync. One speaker at a time, no overlapping dialogue. Keep the same character appearance across shots. Fast pacing, no long intro, clear action readable on a phone. No subtitles, no extra on-screen text, no logos, no watermark. No gore. Keep the entire video in {aspect}. Do not invent extra dialogue or change the ending."""
    idea["thumbnail_prompt"] = f"""Create a striking thumbnail/key visual for Gokil 3D, {aspect} composition. Character mode: {character}. Character design: {character_guide_text}. Scene based on: {idea.get('hook','')}. Title concept: {idea.get('title','')}. Premium stylized 3D animation, expressive exaggerated faces, clear foreground character, funny visual contradiction, rich colors, cinematic lighting, crisp details, high contrast, readable on a mobile screen. Keep character designs consistent with the video prompt. No watermark or logos. Avoid text unless added manually later."""
    idea.setdefault("hashtags", "#Gokil3D #Shorts #Komedi3D #AnimasiLucu")
    return idea

with st.sidebar:
    st.header("Pengaturan Gokil 3D")
    key = get_key()
    st.write("Gemini API:", "✅ Terhubung" if key else "⚠️ Belum diatur")
    model = st.text_input("Model Gemini", "gemini-3.5-flash-lite")
    language_pick = st.selectbox("Bahasa cerita & dialog", LANGUAGES, index=0)
    if language_pick == "Bahasa lain (isi sendiri)":
        language = st.text_input("Masukkan bahasa", "English") or "English"
    else: language = language_pick
    character = st.selectbox("Karakter utama", ["Semar", "Skeleton", "Manusia 3D", "Semar + Skeleton", "Skeleton + Manusia", "Acak sesuai cerita"], index=5)
    style = st.selectbox("Gaya animasi 3D", ["3D kartun sinematik", "3D semi-realistis", "3D slapstick absurd", "3D fantasi lucu"], index=0)
    duration = st.selectbox("Durasi Shorts", ["10 detik", "15 detik", "20 detik", "30 detik"], index=1)
    aspect = st.selectbox("Rasio video", ["9:16", "16:9"], index=0)
    humor = st.selectbox("Jenis komedi", ["Kehidupan sehari-hari", "Absurd dan mengejutkan", "Roasting ringan", "Salah paham", "Plot twist", "Komedi fantasi"], index=0)
    avoid = st.text_input("Hindari cerita/karakter (opsional)")
    st.caption("API key dibaca dari Streamlit Secrets: GEMINI_API_KEY. Jangan masukkan key ke kode publik.")

if "gokil_history" not in st.session_state: st.session_state.gokil_history = []
if "gokil_idea" not in st.session_state: st.session_state.gokil_idea = None

if st.button("🤣 GENERATE CERITA BARU", type="primary", use_container_width=True):
    recent = st.session_state.gokil_history[-12:]
    prompt = f"""Create ONE genuinely original short-form 3D animated comedy idea for a YouTube channel named Gokil 3D.
OUTPUT LANGUAGE: {language}. Write every field and spoken line in {language} (hashtags can remain common social hashtags).
STYLE: {style}. HUMOR: {humor}. DURATION: {duration}. ASPECT RATIO: {aspect}.
CHARACTER MODE: {character}. Character rules: Semar = respectful Javanese wayang-inspired 3D character in traditional attire; Skeleton = funny stylized ivory skeleton, no gore; Manusia 3D = original expressive human characters; combination modes use both named characters as co-leads; Acak sesuai cerita = choose the best fit. Maintain consistent design across shots.
Audience: general audience, clean comedic slapstick and relatable absurdity. Strong visual hook in first 0–2 seconds, clear setup, escalation, unexpected punchline, and a CTA that is naturally part of the joke.
IMPORTANT: make the premise, characters, conflict, dialogue, punchline, and CTA meaningfully different from prior ideas. Do not reuse these recent titles: {json.dumps(recent, ensure_ascii=False)}. Avoid: {avoid or 'none'}.
Dialogue should fit the selected duration, use at most 3 characters, short natural lines, no long intro. Include a CTA spoken by a character and tailor it to the story/punchline. Do not use the exact same CTA wording from previous ideas. No generic standalone “like and subscribe” line.
Return valid JSON only with fields: title, hook, story, dialogue (array of objects with time, speaker, line), punchline, ending, cta_note, hashtags. Ensure the CTA is explicitly one of the dialogue lines."""
    try:
        if not key: raise RuntimeError("GEMINI_API_KEY belum dipasang di Streamlit Secrets.")
        idea = gemini_generate(key, model.strip() or "gemini-3.5-flash-lite", prompt)
        idea = ensure_cta(idea, language)
        idea = build_prompts(idea, style, duration, language, aspect, character)
        st.session_state.gokil_idea = idea
        title = idea.get("title", "")
        if title: st.session_state.gokil_history.append(title)
        st.session_state.gokil_history = st.session_state.gokil_history[-20:]
    except Exception as e:
        idea = random.choice(LOCAL_IDEAS).copy()
        # Deep-copy nested structures so a later run cannot mutate the pool.
        idea = json.loads(json.dumps(idea, ensure_ascii=False))
        idea = ensure_cta(idea, language)
        idea = build_prompts(idea, style, duration, language, aspect, character)
        st.session_state.gokil_idea = idea
        st.warning(f"Gemini belum berhasil: {e}")
        st.info("Aplikasi memakai ide cadangan lokal berbahasa Indonesia. Untuk cerita baru dan bahasa lain, periksa API/kuota lalu generate lagi.")
        st.session_state.gokil_history.append(idea.get("title", ""))
        st.session_state.gokil_history = st.session_state.gokil_history[-20:]

idea = st.session_state.gokil_idea
if idea:
    st.divider()
    st.header(idea.get("title", "Ide Gokil 3D"))
    st.code(idea.get("hashtags", "#Gokil3D #Shorts #Komedi3D"))
    tab1, tab2, tab3, tab4 = st.tabs(["Cerita & Dialog", "Prompt Google Flow", "Prompt Visual/Thumbnail", "Catatan Performa"])
    with tab1:
        st.markdown("**HOOK (0–2 detik)**")
        st.write(idea.get("hook", ""))
        st.markdown("**CERITA**")
        st.write(idea.get("story", ""))
        st.markdown("**DIALOG**")
        for d in idea.get("dialogue", []):
            st.write(f"**{d.get('time','')} | {d.get('speaker','')}** — {d.get('line','')}")
        st.markdown("**PUNCHLINE**")
        st.write(idea.get("punchline", ""))
        st.markdown("**ENDING**")
        st.write(idea.get("ending", ""))
        st.info(idea.get("cta_note", "CTA harus menyatu dengan lelucon dan sesuai cerita."))
    with tab2:
        st.text_area("Salin prompt video ke Google Flow", idea.get("flow_prompt", ""), height=480)
    with tab3:
        st.text_area("Salin prompt visual", idea.get("thumbnail_prompt", ""), height=300)
    with tab4:
        c1,c2,c3 = st.columns(3)
        views = c1.number_input("Views", min_value=0, step=1, key="g_views")
        subs = c2.number_input("Subscriber dari video", min_value=0, step=1, key="g_subs")
        stayed = c3.number_input("Stayed to watch (%)", min_value=0.0, max_value=100.0, step=0.5, key="g_stayed")
        if views:
            st.metric("Subscriber per 1.000 views", f"{subs / views * 1000:.1f}")
        st.caption("Gunakan angka YouTube Studio setelah video tayang; bandingkan beberapa video sebelum mengubah formula.")
    package = {k: idea.get(k) for k in ["title","hashtags","hook","story","dialogue","punchline","ending","cta_note","flow_prompt","thumbnail_prompt"]}
    package["character_mode"] = character
    st.download_button("⬇️ Download paket ide JSON", json.dumps(package, ensure_ascii=False, indent=2), file_name="gokil3d_idea.json", mime="application/json")
else:
    st.markdown("### Cara pakai")
    st.write("1. Pastikan GEMINI_API_KEY tersedia di Streamlit Secrets. 2. Pilih bahasa, gaya animasi, dan durasi. 3. Tekan Generate Cerita Baru. 4. Salin prompt Google Flow untuk membuat video.")
    st.write("Setiap ide harus punya premis baru, dialog pendek, punchline, dan CTA yang menyatu dengan lelucon.")
