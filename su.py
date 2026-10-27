import json, random
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Ôn thi Lịch sử 12", page_icon="📚", layout="centered",
                   initial_sidebar_state="collapsed")

# Ẩn công cụ Streamlit, tăng cỡ chữ, nút nộp bài nổi bên phải
st.markdown("""
<style>
#MainMenu, header, footer, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stHeader"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stSidebar"],
[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"]
{ display: none !important; visibility: hidden !important; }
.block-container { padding-top: 1.5rem; }
html { font-size: 18px; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stRadio"] label,
[data-testid="stRadio"] label p,
[data-testid="stCheckbox"] label p,
[data-testid="stAlert"] p,
[data-testid="stCaptionContainer"] p,
.stButton button p { font-size: 1.1rem !important; line-height: 1.6; }
.st-key-nop_bai_noi,
.element-container:has(.nop-marker) + .element-container,
[data-testid="stElementContainer"]:has(.nop-marker) + [data-testid="stElementContainer"] {
    position: fixed !important; top: 50%; right: 16px; transform: translateY(-50%);
    z-index: 999999; width: auto !important; margin: 0 !important;
}
.element-container:has(.nop-marker), [data-testid="stElementContainer"]:has(.nop-marker) { display: none; }
.st-key-nop_bai_noi button,
[data-testid="stElementContainer"]:has(.nop-marker) + [data-testid="stElementContainer"] button {
    box-shadow: 0 4px 14px rgba(0,0,0,.35); padding: .8rem 1.2rem; border-radius: 999px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load():
    p = Path(__file__).with_name("de_lich_su_12.json")
    return json.loads(p.read_text(encoding="utf-8"))


DATA = load()
MC, TF = DATA["mc"], DATA["tf"]
TF_NAME = "PHẦN 6: TRẮC NGHIỆM ĐÚNG/SAI"
S = st.session_state


def bat_dau(xao):
    mcs, tfs = list(MC), list(TF)
    if xao:
        random.shuffle(mcs)
        random.shuffle(tfs)
    S["ds_cau_hoi"] = [("mc", q) for q in mcs] + [("tf", q) for q in tfs]
    S["xao_tron"] = xao
    S["da_nop"] = False
    S["xem_lai"] = False
    S["ds_tra_loi"] = {}
    S["lan_lam"] = S.get("lan_lam", 0) + 1  # đổi key để xoá đáp án cũ
    st.rerun()


st.title("📚 Ôn thi Lịch sử")

# ---------------- Lựa chọn duy nhất ----------------
c1, c2 = st.columns([2, 1])
shuffle = c1.checkbox("Xáo trộn thứ tự câu", value=False)
if c2.button("🚀 Bắt đầu", type="primary", use_container_width=True):
    bat_dau(shuffle)

if "ds_cau_hoi" not in S:
    st.info("Bấm **Bắt đầu** để làm bài (120 câu trắc nghiệm + 10 câu đúng/sai).")
    st.stop()

items = S["ds_cau_hoi"]
run = S["lan_lam"]
submitted = S["da_nop"]
xem_lai = S.get("xem_lai", False)


def key_mc(q):
    return f"mc{run}_{q['id']}"


def key_tf(q, k):
    return f"tf{run}_{q['id']}_{k}"


def lay(key):
    """Đáp án học sinh chọn: khi đang làm lấy từ widget, sau khi nộp lấy từ bản chụp."""
    return S["ds_tra_loi"].get(key) if submitted else S.get(key)


def tinh_diem():
    r = dict(chua_lam=0, mc_ok=0, mc_n=0, tf_ok=0, tf_n=0, y_ok=0, y_n=0)
    for kind, q in items:
        if kind == "mc":
            r["mc_n"] += 1
            pick = lay(key_mc(q))
            if pick is None:
                r["chua_lam"] += 1
            elif pick == q["ans"]:
                r["mc_ok"] += 1
        else:
            r["tf_n"] += 1
            vals = [lay(key_tf(q, k)) for k in "abcd"]
            if all(v is None for v in vals):
                r["chua_lam"] += 1
            cnt = sum(v == ("Đúng" if q["ans"][k] else "Sai") for k, v in zip("abcd", vals))
            r["y_n"] += 4
            r["y_ok"] += cnt
            if cnt == 4:
                r["tf_ok"] += 1
    r["dung"] = r["mc_ok"] + r["tf_ok"]
    r["tong"] = r["mc_n"] + r["tf_n"]
    r["sai"] = r["tong"] - r["dung"]
    return r


def hien_ket_qua(suffix):
    r = tinh_diem()
    st.subheader("📊 Kết quả bài làm")
    a, b = st.columns(2)
    a.metric("✅ Số câu đúng", f"{r['dung']}/{r['tong']}")
    b.metric("❌ Số câu sai", f"{r['sai']}/{r['tong']}")
    st.caption(
        f"Trắc nghiệm: đúng {r['mc_ok']}/{r['mc_n']} · "
        f"Đúng/Sai: đúng {r['tf_ok']}/{r['tf_n']} câu ({r['y_ok']}/{r['y_n']} ý) · "
        f"Chưa làm: {r['chua_lam']} câu (tính là sai)"
    )
    x, y = st.columns(2)
    if x.button("🔁 Làm lại", key=f"lam_lai_{suffix}", use_container_width=True):
        bat_dau(S["xao_tron"])
    if not xem_lai:
        if y.button("📖 Xem lại bài thi", key=f"xem_lai_{suffix}", type="primary",
                    use_container_width=True):
            S["xem_lai"] = True
            st.rerun()
    else:
        if y.button("⬅️ Về trang kết quả", key=f"ve_kq_{suffix}", use_container_width=True):
            S["xem_lai"] = False
            st.rerun()


# ---------------- Sau khi nộp ----------------
if submitted and not xem_lai:
    hien_ket_qua("kq")
    st.stop()
if submitted and xem_lai:
    hien_ket_qua("tren")
    st.markdown("### 📝 Xem lại bài thi")

# ---------------- Nút nộp bài (nổi bên phải) ----------------
if not submitted:
    st.markdown('<span class="nop-marker"></span>', unsafe_allow_html=True)
    if st.button("📝 Nộp bài", key="nop_bai_noi", type="primary"):
        keys = []
        for kind, q in items:
            keys += [key_mc(q)] if kind == "mc" else [key_tf(q, k) for k in "abcd"]
        S["ds_tra_loi"] = {k: S.get(k) for k in keys}  # chụp lại đáp án trước khi nộp
        S["da_nop"] = True
        S["xem_lai"] = False
        st.rerun()

# ---------------- Danh sách câu hỏi ----------------
last_section = None
for idx, (kind, q) in enumerate(items, 1):
    if not S["xao_tron"]:
        sec = q["section"] if kind == "mc" else TF_NAME
        if sec != last_section:
            st.header(sec)
            last_section = sec

    with st.container(border=True):
        st.markdown(f"**Câu {idx}**")
        if kind == "mc":
            st.write(q["q"])
            keys = list(q["opts"].keys())
            saved = lay(key_mc(q)) if submitted else None
            pick = st.radio(
                "Chọn đáp án", keys, key=key_mc(q),
                index=keys.index(saved) if saved in keys else None,
                format_func=lambda k, q=q: f"{k}. {q['opts'][k]}",
                disabled=submitted, label_visibility="collapsed",
            )
            if submitted:
                pick = saved
                dap_an = f"{q['ans']}. {q['opts'].get(q['ans'], '')}"
                if pick is None:
                    st.warning(f"Bạn chưa trả lời. Đáp án đúng: **{dap_an}**")
                elif pick == q["ans"]:
                    st.success("✅ Chính xác!")
                else:
                    st.error(f"❌ Sai. Bạn chọn **{pick}**. Đáp án đúng: **{dap_an}**")
        else:
            st.info(q["passage"])
            cnt = 0
            for k in "abcd":
                st.write(f"**{k})** {q['stmts'][k]}")
                opts = ["Đúng", "Sai"]
                saved = lay(key_tf(q, k)) if submitted else None
                v = st.radio(
                    k, opts, key=key_tf(q, k), horizontal=True,
                    index=opts.index(saved) if saved in opts else None,
                    disabled=submitted, label_visibility="collapsed",
                )
                if submitted:
                    v = saved
                truth = "Đúng" if q["ans"][k] else "Sai"
                if v == truth:
                    cnt += 1
                if submitted:
                    if v is None:
                        st.caption(f"⚠️ Chưa chọn — đáp án đúng: **{truth}**")
                    elif v == truth:
                        st.caption("✅ Đúng")
                    else:
                        st.caption(f"❌ Bạn chọn {v} — đáp án đúng: **{truth}**")
            if submitted:
                st.markdown(f"Đúng **{cnt}/4** ý")

if submitted:
    st.divider()
    hien_ket_qua("duoi")