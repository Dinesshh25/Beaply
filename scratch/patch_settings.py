import re

with open('test_fiture.py', 'r', encoding='utf-8') as f:
    text = f.read()

settings_new_code = '''class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, profil_id, logout_callback, apply_pref_callback):
        super().__init__(master)
        self.title("Settings")
        self.geometry("600x700")
        self.profil_id = profil_id
        self.logout = logout_callback
        self.apply_pref_callback = apply_pref_callback
        self._bhs = get_bahasa(profil_id)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build()

    def _build(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        bhs = self._bhs

        # TOP BAR
        bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(bar, text=t("judul_settings", bhs), font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_DARK).pack(side="left")

        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # --- Account & Security ---
        ctk.CTkLabel(scroll, text=t("lbl_acc_sec", bhs), font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_DARK).pack(anchor="w", pady=(10, 5))
        sec_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        sec_card.pack(fill="x", pady=5)
        
        pw_r = ctk.CTkFrame(sec_card, fg_color="transparent")
        pw_r.pack(fill="x", padx=15, pady=15)
        
        txt_box = ctk.CTkFrame(pw_r, fg_color="transparent")
        txt_box.pack(side="left")
        ctk.CTkLabel(txt_box, text=t("lbl_change_pw", bhs), font=ctk.CTkFont(weight="bold"), text_color=TEXT_DARK, anchor="w").pack(fill="x")
        ctk.CTkLabel(txt_box, text=t("lbl_desc_pw", bhs), text_color="gray", anchor="w").pack(fill="x")
        
        ctk.CTkButton(pw_r, text=">", width=30, fg_color="transparent", text_color=TEXT_DARK, hover_color=BTN_PALE, command=self._popup_change_pw).pack(side="right")
        
        # --- Display ---
        ctk.CTkLabel(scroll, text=t("lbl_display", bhs), font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_DARK).pack(anchor="w", pady=(20, 5))
        disp_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        disp_card.pack(fill="x", pady=5)
        
        pref = ambil_preferensi(self.profil_id)
            
        def settings_row(parent, title, desc, widget):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=15)
            txt_bx = ctk.CTkFrame(r, fg_color="transparent")
            txt_bx.pack(side="left")
            ctk.CTkLabel(txt_bx, text=title, font=ctk.CTkFont(weight="bold"), text_color=TEXT_DARK, anchor="w").pack(fill="x")
            ctk.CTkLabel(txt_bx, text=desc, text_color="gray", anchor="w").pack(fill="x")
            widget.pack(side="right", in_=r)
            
        t_frame = ctk.CTkSegmentedButton(disp_card, values=[t("opt_light", bhs), t("opt_dark", bhs), t("opt_system", bhs)], command=self._change_theme)
        val = t("opt_" + pref.get("tema", "system"), bhs)
        try: t_frame.set(val) 
        except: pass
        settings_row(disp_card, t("lb_tema", bhs), t("desc_theme", bhs), t_frame)
        
        l_frame = ctk.CTkComboBox(disp_card, values=["Bahasa Indonesia", "English"], command=self._change_lang)
        l_frame.set("Bahasa Indonesia" if pref.get("bahasa") == "id" else "English")
        settings_row(disp_card, t("lb_bahasa", bhs), t("desc_lang", bhs), l_frame)
        
        s_frame = ctk.CTkSegmentedButton(disp_card, values=[t("opt_small", bhs), t("opt_medium", bhs), t("opt_large", bhs)])
        val = t("opt_" + pref.get("ukuran_teks", "medium"), bhs)
        try: s_frame.set(val)
        except: pass
        settings_row(disp_card, t("lb_ukuran", bhs), t("desc_size", bhs), s_frame)
        
        del_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        del_card.pack(fill="x", pady=20)
        ctk.CTkButton(del_card, text=t("btn_hapus", bhs), fg_color="transparent", text_color="red", hover_color="#fceae8", command=self._do_hapus).pack(pady=15)

    def _save_pref_partial(self, key, value):
        pref = ambil_preferensi(self.profil_id)
        pref[key] = value
        simpan_preferensi(self.profil_id, pref["tema"], pref["ukuran_teks"], pref["bahasa"])

    def _change_theme(self, choice):
        bhs = self._bhs
        val_map = {t("opt_light", bhs): "light", t("opt_dark", bhs): "dark", t("opt_system", bhs): "system"}
        act = val_map.get(choice, "system")
        if act in ["light", "dark", "system"]:
            ctk.set_appearance_mode(act)
        self._save_pref_partial("tema", act)

    def _change_lang(self, choice):
        act = "id" if choice == "Bahasa Indonesia" else "en"
        self._save_pref_partial("bahasa", act)
        self._bhs = act
        for w in self.winfo_children(): w.destroy()
        self._build()
        if self.apply_pref_callback: self.apply_pref_callback()

    def _do_hapus(self):
        bhs = self._bhs
        if konfirm_yesno(self, t("konfirm_judul", bhs), t("konfirm_teks", bhs)):
            ok, msg = hapus_akun(self.profil_id, True)
            if ok:
                show_info(self, t("akun_dihapus", bhs), t("ok_hapus", bhs))
                self.destroy()
                self.logout()
            else:
                show_error(self, t("gagal", bhs), msg)

    def _popup_change_pw(self):
        bhs = self._bhs
        top = ctk.CTkToplevel(self)
        top.title(t("lbl_change_pw", bhs))
        top.geometry("350x300")
        top.transient(self)
        top.grab_set()
        
        ctk.CTkLabel(top, text=t("lbl_change_pw", bhs), font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)
        
        e1 = ctk.CTkEntry(top, placeholder_text=t("lbl_old_pw", bhs), show="*")
        e1.pack(pady=5, padx=20, fill="x")
        e2 = ctk.CTkEntry(top, placeholder_text=t("lbl_new_pw", bhs), show="*")
        e2.pack(pady=5, padx=20, fill="x")
        e3 = ctk.CTkEntry(top, placeholder_text=t("lbl_conf_pw", bhs), show="*")
        e3.pack(pady=5, padx=20, fill="x")
        
        def save_pw():
            old = e1.get()
            nw = e2.get()
            cn = e3.get()
            if not old or not nw or not cn:
                return show_error(top, t("gagal", bhs), "All fields required!")
            if nw != cn:
                return show_error(top, t("gagal", bhs), "New passwords do not match!")
            p = tampil_profil(self.profil_id)
            if p["password"] != old:
                return show_error(top, t("gagal", bhs), t("err_wrong_pw", bhs))
            ok, msg = ganti_password(self.profil_id, nw)
            if ok:
                show_info(top, t("berhasil", bhs), msg)
                top.destroy()
            else:
                show_error(top, t("gagal", bhs), msg)
                
        ctk.CTkButton(top, text=t("btn_change_pw", bhs), fg_color=BTN_GREEN, text_color=TEXT_DARK, command=save_pw).pack(pady=20)
'''

text = re.sub(r'class SettingsWindow\(ctk\.CTkToplevel\):.*?# ════════════════════════════════════════════════════════════\n# LAYOUT: Sidebar \+ Content Area', settings_new_code + '\n# ════════════════════════════════════════════════════════════\n# LAYOUT: Sidebar + Content Area', text, flags=re.DOTALL)

with open('test_fiture.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Replaced SettingsWindow!')
