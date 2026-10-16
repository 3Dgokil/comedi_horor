import os, json, random, requests, re
import streamlit as st

st.set_page_config(page_title="Gokil Shorts Studio — Live Action", page_icon="🎬", layout="wide")
st.title("🎬 Gokil Shorts Studio — Live Action")
st.caption("Komedi live-action fotorealistis • hook cepat • punchline kuat • CTA menyatu • loop sinematik")

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
    # Strengthen the final line even when Gemini returned a weak/generic CTA.
    ds = idea.get("dialogue") or []
    if not ds:
        ds = [{"time":"AKHIR", "speaker":"KARAKTER", "line":""}]
    context = (str(idea.get("title", "")) + " " + str(idea.get("story", "")) + " " + str(idea.get("punchline", ""))).lower()
    if language == "English":
        line = "Hit subscribe—unless you want this disaster to come back for YOU!"
    elif language == "Português do Brasil":
        line = "Se inscreve agora—ou esse desastre volta pra sua casa!"
    elif language == "Español":
        line = "¡Suscríbete ya, o este desastre vuelve a tu casa!"
    elif language == "Bahasa Melayu":
        line = "Langgan sekarang—kalau tak, masalah ni datang rumah kau!"
    elif language == "हिन्दी (Hindi)":
        line = "अभी सब्सक्राइब करो, वरना ये मुसीबत तुम्हारे घर आएगी!"
    elif language == "日本語 (Japanese)":
        line = "今すぐ登録して！じゃないと、この騒動が家まで来るよ！"
    else:
        if any(k in context for k in ["mie", "masak", "chef", "panci", "dapur"]):
            line = "SUBSCRIBE SEKARANG—kalau nggak, chef ini masak lagi di rumah lu!"
        elif any(k in context for k in ["robot", "utang", "tagihan", "saldo", "cicilan"]):
            line = "PENCET SUBSCRIBE—atau robot ini datang nagih ke rumah lu!"
        elif any(k in context for k in ["kucing", "bos", "rapat", "lembur", "kantor"]):
            line = "SUBSCRIBE SEKARANG—sebelum bos ini nyuruh lu lembur seumur hidup!"
        elif any(k in context for k in ["pendekar", "jurus", "naga", "bertarung"]):
            line = "SUBSCRIBE—sebelum jurus berikutnya malah kena ke lu!"
        elif any(k in context for k in ["dompet", "sultan", "traktir", "uang", "kaya"]):
            line = "SUBSCRIBE DULU—kalau nggak, lu yang wajib traktir episode berikutnya!"
        else:
            line = random.choice([
                "SUBSCRIBE SEKARANG—kalau nggak, gue balik lagi buat nagih langsung!",
                "PENCET SUBSCRIBE! Kalau nggak, plot twist berikutnya nyasar ke rumah lu!",
                "SUBSCRIBE, JANGAN CUMA NGAKAK! Besok masalahnya bisa jadi punya lu!",
                "Berani nonton sampai habis? Buktiin—SUBSCRIBE sekarang!",
            ])
    # Keep the CTA as the last spoken line, replacing weak/incorrect final lines.
    ds[-1]["line"] = line
    ds[-1].setdefault("time", "AKHIR")
    ds[-1].setdefault("speaker", "KARAKTER")
    idea["dialogue"] = ds
    idea["cta_note"] = "CTA dibuat tegas dan dikaitkan dengan tema cerita; selalu menjadi dialog terakhir."
    return idea

def build_prompts(idea, style, duration, language, aspect, character):
    dialogue = "\n".join(f'{d.get("time", "")} | {d.get("speaker", "")}: "{d.get("line", "")}"' for d in idea.get("dialogue", []))
    character_guide = {
        "Manusia realistis": "Real Indonesian adult actors filmed as live action. Natural skin pores, real hair strands, realistic eyes and teeth, correct anatomy and hands, subtle facial micro-expressions, authentic clothing and physical behavior. Keep identical face, age, hairstyle, outfit and body proportions in every shot.",
        "Manusia + Skeleton realistis": "One photorealistic Indonesian adult actor and one believable practical skeleton character. The human must look like real live-action footage. Skeleton has anatomically plausible ivory bones, realistic material and weight, expressive but physically believable movement; not a cartoon mascot. Keep both designs and scale identical in every shot.",
        "Semar live-action + Manusia": "A real adult performer wearing a high-quality, realistic Semar-inspired Javanese theatrical costume and makeup, alongside a photorealistic Indonesian adult actor. Treat Semar respectfully. Both look filmed on a real set, not animated. Preserve exact face, costume, makeup and proportions across all shots.",
        "Semar live-action": "A real adult performer in a detailed, realistic Semar-inspired Javanese theatrical costume and makeup, filmed live-action on a real set. Respectful cultural portrayal; natural fabric, believable makeup, real skin texture, consistent face and costume.",
        "Skeleton realistis": "A physically believable skeleton character filmed as live-action practical creature footage: anatomically plausible ivory bones, subtle realistic surface detail, correct joints, natural weight and shadows. No oversized cartoon skull, no toy look, no exaggerated proportions, no gore.",
        "Acak sesuai cerita": "Choose the smallest suitable cast from photorealistic live-action Indonesian adult actors, a realistic practical skeleton character, or a respectful Semar-inspired performer in realistic costume. All must look filmed in the real world, never animated."
    }
    character_guide_text = character_guide.get(character, character_guide["Acak sesuai cerita"])
    visual_rules = """VISUAL DNA — MATCH THE PHOTOREALISTIC CINEMATIC LOOK OF CADAS RESONANCE:
This must look like real live-action cinema captured with a professional camera, not an animation. Photorealistic people, authentic skin pores and fine lines, natural eyes, real hair, physically correct hands, real cloth texture, practical lighting, cinematic lens depth of field, believable shadows, natural motion blur, realistic camera movement, detailed real environments. Use a grounded cinematic color grade and strong visual storytelling.
ABSOLUTE NEGATIVES: NO 3D animation, NO cartoon, NO Pixar, NO anime, NO game render, NO plastic skin, NO toy appearance, NO exaggerated proportions, NO glossy CGI character, NO artificial doll face, NO floating body parts, NO morphing, NO identity drift, NO costume changes, NO extra fingers, NO duplicated characters. If a skeleton is present, make it a believable practical creature in the same real environment, with stable size and anatomy; do not turn the human into an animated character.
CONTINUITY LOCK: same actor identity, face, hairstyle, clothes, body size, skeleton skull size, bone shape, props, set layout and lighting in every shot. Prefer 2–3 coherent shots over many disconnected cuts. Every movement must have a clear physical cause and realistic contact with objects."""
    idea["flow_prompt"] = f"""Create a {duration} {aspect} vertical YouTube Shorts comedy video. Genre: photorealistic live-action comedy with cinematic realism.
CHARACTER MODE: {character}
CHARACTER IDENTITY LOCK: {character_guide_text}
{visual_rules}
STORY GOAL: immediate visual hook in the first second; clear setup; escalation; a surprising, genuinely funny punchline; then a short CTA that is part of the joke. Avoid random movement or unrelated visual gags. Make the action easy to understand on a phone screen.
CTA: preserve the final dialogue exactly. The last spoken line must directly say subscribe and connect to the joke's specific consequence or challenge. No channel name, no generic polite CTA. Speak naturally, with accurate Indonesian lip sync, one speaker at a time.
LOOP DESIGN: establish one repeatable action in the first second (for example, a hand reaching for a cup, a character turning toward camera, or a door beginning to open). Resolve the joke, then in the final second physically return to the same starting pose, camera distance, angle, framing, light, background and direction of motion. No end card, no freeze, no fade, no black frame, no pause. The CTA must finish before the final loop-matching moment. Keep the same continuous scene wherever possible; avoid unnecessary camera cuts.
TITLE: {idea.get('title','')}
OPENING HOOK: {idea.get('hook','')}
STORY: {idea.get('story','')}
DIALOGUE — speak exactly as written; do not omit, reorder, paraphrase, or add lines:
{dialogue}
PUNCHLINE: {idea.get('punchline','')}
ENDING ACTION: {idea.get('ending','')}
LANGUAGE: {language}. Natural performance, believable reactions, precise lip sync, clear sound, no overlapping dialogue. No subtitles, no on-screen text, no logos, no watermark. Keep the entire video {aspect}. No gore. Do not add a separate subscribe screen. This is a target, not a guarantee: if the generated ending does not match the opening, regenerate or trim the join."""
    idea["thumbnail_prompt"] = f"Photorealistic live-action cinematic key visual, {aspect} vertical composition. Based on this scene: {idea.get('hook','')}. Characters: {character_guide_text}. Match the live-action cinematic look: real skin texture, natural facial detail, believable lighting and shadows, authentic materials, realistic lens depth of field, expressive but natural reaction, a single clear visual joke readable on mobile. Absolutely no 3D animation, cartoon, anime, toy-like skin, plastic CGI look, text, watermark or logo. Keep actor identity, costume and props consistent with the video."
    idea["hashtags"] = idea.get("hashtags") or "#Shorts #Komedi #LiveAction #ComedyShorts #PlotTwist"
    return idea

with st.sidebar:
    st.header("Pengaturan Gokil Live Action")
    key = get_key()
    st.write("Gemini API:", "✅ Terhubung" if key else "⚠️ Belum diatur")
    model = st.text_input("Model Gemini", "gemini-3.1-PRO")
    language_pick = st.selectbox("Bahasa cerita & dialog", LANGUAGES, index=0)
    if language_pick == "Bahasa lain (isi sendiri)":
        language = st.text_input("Masukkan bahasa", "English") or "English"
    else: language = language_pick
    character = st.selectbox("Karakter live-action", ["Manusia realistis", "Manusia + Skeleton realistis", "Skeleton realistis", "Semar live-action", "Semar live-action + Manusia", "Acak sesuai cerita"], index=1)
    style = "Photorealistic live-action cinematic comedy (Cadas Resonance realism)"
    duration = st.selectbox("Durasi Shorts", ["10 detik", "15 detik", "20 detik", "30 detik"], index=1)
    aspect = st.selectbox("Rasio video", ["9:16", "16:9"], index=0)
    humor = st.selectbox("Jenis komedi", ["Kehidupan sehari-hari", "Absurd dan mengejutkan", "Roasting ringan", "Salah paham", "Plot twist", "Komedi fantasi"], index=0)
    avoid = st.text_input("Hindari cerita/karakter (opsional)")
    st.caption("API key dibaca dari Streamlit Secrets: GEMINI_API_KEY. Jangan masukkan key ke kode publik.")

if "gokil_history" not in st.session_state: st.session_state.gokil_history = []
if "gokil_idea" not in st.session_state: st.session_state.gokil_idea = None

if st.button("🤣 GENERATE CERITA BARU", type="primary", use_container_width=True):
    recent = st.session_state.gokil_history[-12:]
    prompt = f"""Create ONE genuinely original photorealistic LIVE-ACTION comedy Short. It must look like real cinema footage, not 3D animation.
OUTPUT LANGUAGE: {language}. Write every field and spoken line in {language} (hashtags can remain common social hashtags).
VISUAL STYLE: {style}. Never use cartoon, 3D animation, Pixar, anime, game render, or plastic-looking CGI humans. HUMOR: {humor}. DURATION: {duration}. ASPECT RATIO: {aspect}.
CHARACTER MODE: {character}. Use photorealistic live-action Indonesian adult actors. Skeleton must look like a believable practical creature filmed on set, not a cartoon or toy. Semar must be a real performer in realistic theatrical costume and makeup. Keep exact identity, face, clothes, scale and anatomy across shots. No 3D animation, no cartoon, no CGI-render aesthetic.
Audience: general audience, clean comedic slapstick and relatable absurdity. Strong visual hook in the first 0–1 second, setup by 3 seconds, escalation, unexpected visual punchline, and a bold CTA integrated into the joke. The CTA must not sound like an advertisement pasted on afterward. Never mention the channel name or brand in dialogue. Design a seamless loop: final action and pose connect back to the opening frame; no fade, pause, black frame, end card, or abrupt stop.
IMPORTANT: make the premise, characters, conflict, dialogue, punchline, and CTA meaningfully different from prior ideas. Do not reuse these recent titles: {json.dumps(recent, ensure_ascii=False)}. Avoid: {avoid or 'none'}.
Dialogue should fit the selected duration, use at most 3 characters, short natural lines, no long intro. The final dialogue line MUST be a powerful, specific CTA: say “subscribe” explicitly and connect it to a funny consequence, dare, or cliffhanger from this exact story. It must sound bold and memorable, not weak or polite. No generic “like and subscribe” line. Do not mention the channel name. NEVER mention the channel name “Gokil 3D” or any channel/brand name in dialogue or CTA. Make the ending a seamless loop: the final action/pose should connect back to the opening hook, with no fade-out, pause, black frame, end card, or abrupt stop. Ideally the last frame mirrors the first frame so replay feels continuous.
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
        st.session_state.gokil_idea = None
        st.error(f"Gemini gagal membuat cerita baru: {e}")
        st.info("Tidak ada template pengganti yang ditampilkan agar hasil tidak berulang. Periksa GEMINI_API_KEY, kuota, dan nama model lalu coba lagi.")

idea = st.session_state.gokil_idea
if idea:
    st.divider()
    st.header(idea.get("title", "Ide Komedi Live Action"))
    st.code(idea.get("hashtags", "#Shorts #Komedi #LiveAction #ComedyShorts"))
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
    st.write("Setiap ide harus punya premis baru, dialog pendek, punchline, CTA yang menyatu, dan visual live-action fotorealistis.")
