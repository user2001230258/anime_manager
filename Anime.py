import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import os
from PIL import Image, ImageTk
from io import BytesIO
import threading
import time
from functools import lru_cache

class QuanLyAnime:
    def __init__(self):
        self.cuaSo = tk.Tk()
        self.cuaSo.title("Quản Lý Anime")
        self.cuaSo.geometry("1200x800")
        self.cuaSo.resizable(True, True)
        self.khoiTaoTepDuLieu()
        self.boNhoDemHinhAnh = {}
        self.danhSachHienThiHienTai = []
        self.boNhoDemApi = {}
        self.hienThiManHinhDangNhap()

    def khoiTaoTepDuLieu(self):
        if not os.path.exists('nguoi_dung.json'):
            with open('nguoi_dung.json', 'w') as f:
                json.dump({
                    "admin": {"mat_khau": "admin123", "vai_tro": "admin", "yeu_thich": []},
                    "nguoi_dung": {"mat_khau": "user123", "vai_tro": "nguoi_dung", "yeu_thich": []}
                }, f, indent=4)
        if not os.path.exists('du_lieu_anime.json'):
            with open('du_lieu_anime.json', 'w') as f:
                json.dump([], f)

    def hienThiManHinhTai(self):
        self.khungTai = ttk.Frame(self.cuaSo, style='Tai.TFrame')
        self.khungTai.place(relx=0, rely=0, relwidth=1, relheight=1)
        ttk.Label(self.khungTai, text="Đang tải dữ liệu...", font=('Arial', 14)).place(relx=0.5, rely=0.5, anchor='center')

    def anManHinhTai(self):
        if hasattr(self, 'khungTai'):
            self.khungTai.destroy()

    def nhiemVuNen(self, nhiemVu, *doiSo):
        self.hienThiManHinhTai()
        try:
            ketQua = nhiemVu(*doiSo)
            self.cuaSo.after(0, lambda: self.nhiemVuHoanThanh(ketQua))
        except Exception as e:
            self.cuaSo.after(0, lambda: self.nhiemVuThatBai(str(e)))

    def nhiemVuHoanThanh(self, ketQua):
        self.anManHinhTai()
        if ketQua is not None:
            self.danhSachHienThiHienTai = ketQua
            self.hienThiLuoiAnime(ketQua)

    def nhiemVuThatBai(self, thongBaoLoi):
        self.anManHinhTai()
        messagebox.showerror("Lỗi", thongBaoLoi)

    def _taiHinhNen(self, tenTep, kichThuoc):
        if not os.path.exists(tenTep):
            raise FileNotFoundError(f"Không tìm thấy tệp {tenTep}")
        hinh = Image.open(tenTep).resize(kichThuoc, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(hinh)

    def hienThiManHinhDangNhap(self):
        for widget in self.cuaSo.winfo_children():
            widget.destroy()
        self.nhanHinhNen = tk.Label(self.cuaSo)
        self.nhanHinhNen.place(relx=0, rely=0, relwidth=1, relheight=1)
        try:
            self.anhHinhNen = self._taiHinhNen("a2.png", (1920, 1200))
            self.nhanHinhNen.configure(image=self.anhHinhNen)
            self.nhanHinhNen.image = self.anhHinhNen
            self.nhanHinhNen.lower()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hình nền: {str(e)}")
            return

        khungDangNhap = ttk.Frame(self.cuaSo)
        khungDangNhap.place(relx=0.5, rely=0.5, anchor='center')
        try:
            self.anhHinhNenKhung = self._taiHinhNen("a1.png", (300, 200))
            tk.Label(khungDangNhap, image=self.anhHinhNenKhung).grid(row=0, column=0, rowspan=4, columnspan=2, sticky="nsew")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hình nền khung đăng nhập: {str(e)}")
            return

        ttk.Label(khungDangNhap, text="Tên người dùng:").grid(row=0, column=0, padx=5, pady=5)
        oNhapTenNguoiDung = ttk.Entry(khungDangNhap)
        oNhapTenNguoiDung.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(khungDangNhap, text="Mật khẩu:").grid(row=1, column=0, padx=5, pady=5)
        oNhapMatKhau = ttk.Entry(khungDangNhap, show="*")
        oNhapMatKhau.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(khungDangNhap, text="Đăng nhập", command=lambda: self.dangNhap(oNhapTenNguoiDung.get(), oNhapMatKhau.get())).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(khungDangNhap, text="Đăng ký", command=self.hienThiManHinhDangKy).grid(row=3, column=0, columnspan=2)

    def hienThiManHinhDangKy(self):
        for widget in self.cuaSo.winfo_children():
            widget.destroy()
        self.nhanHinhNen = tk.Label(self.cuaSo)
        self.nhanHinhNen.place(relx=0, rely=0, relwidth=1, relheight=1)
        try:
            self.anhHinhNen = self._taiHinhNen("a2.png", (1570, 900))
            self.nhanHinhNen.configure(image=self.anhHinhNen)
            self.nhanHinhNen.image = self.anhHinhNen
            self.nhanHinhNen.lower()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hình nền: {str(e)}")
            return

        khungDangKy = ttk.Frame(self.cuaSo)
        khungDangKy.place(relx=0.5, rely=0.5, anchor='center')
        try:
            self.anhHinhNenKhungDangKy = self._taiHinhNen("a1.png", (300, 250))
            tk.Label(khungDangKy, image=self.anhHinhNenKhungDangKy).grid(row=0, column=0, rowspan=5, columnspan=2, sticky="nsew")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hình nền khung đăng ký: {str(e)}")
            return

        ttk.Label(khungDangKy, text="Tên người dùng:").grid(row=0, column=0, padx=5, pady=5)
        oNhapTenNguoiDung = ttk.Entry(khungDangKy)
        oNhapTenNguoiDung.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(khungDangKy, text="Mật khẩu:").grid(row=1, column=0, padx=5, pady=5)
        oNhapMatKhau = ttk.Entry(khungDangKy, show="*")
        oNhapMatKhau.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(khungDangKy, text="Xác nhận mật khẩu:").grid(row=2, column=0, padx=5, pady=5)
        oNhapXacNhanMatKhau = ttk.Entry(khungDangKy, show="*")
        oNhapXacNhanMatKhau.grid(row=2, column=1, padx=5, pady=5)

        def dangKy():
            ten, mk, xacNhan = oNhapTenNguoiDung.get(), oNhapMatKhau.get(), oNhapXacNhanMatKhau.get()
            if not (ten and mk and xacNhan):
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ các trường")
                return
            if mk != xacNhan:
                messagebox.showerror("Lỗi", "Mật khẩu không khớp")
                return
            with open('nguoi_dung.json', 'r') as f:
                nguoiDung = json.load(f)
            if ten in nguoiDung:
                messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại")
                return
            nguoiDung[ten] = {"mat_khau": mk, "vai_tro": "nguoi_dung", "yeu_thich": []}
            with open('nguoi_dung.json', 'w') as f:
                json.dump(nguoiDung, f, indent=4)
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            self.hienThiManHinhDangNhap()

        ttk.Button(khungDangKy, text="Đăng ký", command=dangKy).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(khungDangKy, text="Quay lại đăng nhập", command=self.hienThiManHinhDangNhap).grid(row=4, column=0, columnspan=2)

    def dangNhap(self, tenNguoiDung, matKhau):
        with open('nguoi_dung.json', 'r') as f:
            nguoiDung = json.load(f)
        if tenNguoiDung in nguoiDung and nguoiDung[tenNguoiDung]["mat_khau"] == matKhau:
            self.nguoiDungHienTai = tenNguoiDung
            self.vaiTroHienTai = nguoiDung[tenNguoiDung]["vai_tro"]
            self.danhSachYeuThichNguoiDungHienTai = nguoiDung[tenNguoiDung].get("yeu_thich", [])
            self.hienThiManHinhChinh()
            threading.Thread(target=lambda: self.nhiemVuNen(self.layTopAnime)).start()
        else:
            messagebox.showerror("Lỗi", "Tên người dùng hoặc mật khẩu không đúng")

    def _taoKhungCuon(self, khungCha):
        khungCha.columnconfigure(0, weight=1)
        khungCha.rowconfigure(0, weight=1)
        vungVe = tk.Canvas(khungCha)
        thanhCuon = ttk.Scrollbar(khungCha, orient="vertical", command=vungVe.yview)
        khungCoTheCuon = ttk.Frame(vungVe)
        khungCoTheCuon.columnconfigure(0, weight=1)
        khungCoTheCuon.bind("<Configure>", lambda e: vungVe.configure(scrollregion=vungVe.bbox("all")))
        if self.cuaSo.tk.call('tk', 'windowingsystem') == 'win32':
            vungVe.bind_all("<MouseWheel>", lambda e: vungVe.yview_scroll(int(-1*(e.delta/120)), "units"))
        else:
            vungVe.bind_all("<Button-4>", lambda e: vungVe.yview_scroll(-1, "units"))
            vungVe.bind_all("<Button-5>", lambda e: vungVe.yview_scroll(1, "units"))
        vungVe.create_window((0, 0), window=khungCoTheCuon, anchor="nw")
        vungVe.configure(yscrollcommand=thanhCuon.set)
        vungVe.grid(row=0, column=0, sticky="nsew")
        thanhCuon.grid(row=0, column=1, sticky="ns")
        return khungCoTheCuon

    def hienThiManHinhChinh(self):
        self.laCheDoYeuThich = False
        for widget in self.cuaSo.winfo_children():
            widget.destroy()
        khungChinh = ttk.Frame(self.cuaSo)
        khungChinh.pack(expand=True, fill='both', padx=10, pady=10)

        khungTimKiem = ttk.Frame(khungChinh)
        khungTimKiem.pack(fill='x', pady=5)
        ttk.Label(khungTimKiem, text="Tìm kiếm Anime:").pack(side='left', padx=5)
        self.oNhapTimKiem = ttk.Entry(khungTimKiem, width=40)
        self.oNhapTimKiem.pack(side='left', padx=5)
        self.oNhapTimKiem.bind('<Return>', lambda e: self.timKiemAnimeApi())
        ttk.Button(khungTimKiem, text="Tìm kiếm", command=self.timKiemAnimeApi).pack(side='left', padx=5)
        ttk.Label(khungTimKiem, text="Sắp xếp theo:").pack(side='left', padx=5)
        luaChonSapXep = ["Điểm số", "Số tập", "Tiêu đề"]
        self.bienSapXep = tk.StringVar(value="Điểm số")
        ttk.OptionMenu(khungTimKiem, self.bienSapXep, "Điểm số", *luaChonSapXep, command=lambda _: self.sapXepAnime()).pack(side='left', padx=5)

        khungCheDoXem = ttk.Frame(khungChinh)
        khungCheDoXem.pack(fill='x', pady=5)
        bienCheDoXem = tk.StringVar(value="tat_ca")
        ttk.Radiobutton(khungCheDoXem, text="Tất cả Anime", variable=bienCheDoXem, value="tat_ca", command=self.chuyenSangCheDoTatCa).pack(side='left', padx=5)
        ttk.Radiobutton(khungCheDoXem, text="Yêu thích", variable=bienCheDoXem, value="yeu_thich", command=self.hienThiYeuThich).pack(side='left', padx=5)

        khungNoiDung = ttk.Frame(khungChinh)
        khungNoiDung.pack(expand=True, fill='both')
        self.khungCoTheCuon = self._taoKhungCuon(khungNoiDung)

        khungNut = ttk.Frame(khungChinh)
        khungNut.pack(fill='x', pady=10)
        ttk.Button(khungNut, text="Làm mới Top Anime", command=lambda: threading.Thread(target=lambda: self.nhiemVuNen(self.layTopAnime)).start()).pack(side='left', padx=5)
        if self.vaiTroHienTai == "admin":
            ttk.Button(khungNut, text="Quản lý người dùng", command=self.hienThiManHinhQuanLyNguoiDung).pack(side='left', padx=5)
        ttk.Button(khungNut, text="Đăng xuất", command=self.hienThiManHinhDangNhap).pack(side='right', padx=5)

    def hienThiManHinhQuanLyNguoiDung(self):
        for widget in self.cuaSo.winfo_children():
            widget.destroy()
        khungQuanLy = ttk.Frame(self.cuaSo)
        khungQuanLy.pack(expand=True, fill='both', padx=10, pady=10)
        ttk.Label(khungQuanLy, text="Quản lý người dùng", font=('Arial', 16, 'bold')).pack(pady=10)

        khungDanhSach = ttk.Frame(khungQuanLy)
        khungDanhSach.pack(expand=True, fill='both')
        khungCoTheCuon = self._taoKhungCuon(khungDanhSach)

        try:
            with open('nguoi_dung.json', 'r') as f:
                nguoiDung = json.load(f)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc danh sách người dùng: {str(e)}")
            return

        for hang, (tenNguoiDung, thongTin) in enumerate(nguoiDung.items()):
            khungNguoiDung = ttk.Frame(khungCoTheCuon, width=600)
            khungNguoiDung.grid(row=hang, column=0, padx=10, pady=5, sticky="ew")
            khungNguoiDung.grid_propagate(False)
            khungVien = ttk.Frame(khungNguoiDung, style='The.TFrame')
            khungVien.pack(expand=True, fill='both', padx=5, pady=5)
            ttk.Label(khungVien, text=f"Tên người dùng: {tenNguoiDung}", font=('Arial', 12)).pack(anchor='w', padx=10)
            ttk.Label(khungVien, text=f"Vai trò: {thongTin['vai_tro']}", font=('Arial', 12)).pack(anchor='w', padx=10)
            ttk.Label(khungVien, text=f"Số anime yêu thích: {len(thongTin.get('yeu_thich', []))}", font=('Arial', 12)).pack(anchor='w', padx=10)
            if tenNguoiDung != self.nguoiDungHienTai:
                ttk.Button(khungVien, text="Xóa", command=lambda t=tenNguoiDung: self.xoaNguoiDung(t)).pack(anchor='e', padx=10, pady=5)

        khungNut = ttk.Frame(khungQuanLy)
        khungNut.pack(fill='x', pady=10)
        ttk.Button(khungNut, text="Quay lại", command=self.hienThiManHinhChinh).pack(side='right', padx=5)

    def xoaNguoiDung(self, tenNguoiDung):
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa người dùng '{tenNguoiDung}' không?"):
            return
        try:
            with open('nguoi_dung.json', 'r') as f:
                nguoiDung = json.load(f)
            if tenNguoiDung in nguoiDung:
                del nguoiDung[tenNguoiDung]
            with open('nguoi_dung.json', 'w') as f:
                json.dump(nguoiDung, f, indent=4)
            messagebox.showinfo("Thành công", f"Đã xóa người dùng '{tenNguoiDung}' thành công!")
            self.hienThiManHinhQuanLyNguoiDung()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa người dùng: {str(e)}")

    @lru_cache(maxsize=100)
    def layHinhAnh(self, url):
        try:
            phanHoi = requests.get(url)
            hinhAnh = Image.open(BytesIO(phanHoi.content)).resize((200, 300), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(hinhAnh)
        except Exception:
            return None

    def layTopAnime(self):
        try:
            khoaBoNhoDem = "top_anime"
            if khoaBoNhoDem in self.boNhoDemApi:
                return self.boNhoDemApi[khoaBoNhoDem]
            time.sleep(0.5)
            phanHoi = requests.get("https://api.jikan.moe/v4/top/anime")
            if phanHoi.status_code != 200:
                raise Exception("Không thể lấy dữ liệu từ API")
            duLieuAnime = phanHoi.json()['data']
            animeDaXuLy = [
                {
                    'tieu_de': anime['title'],
                    'diem_so': str(anime.get('score', 'N/A')),
                    'so_tap': str(anime.get('episodes', 'N/A')),
                    'trang_thai': anime.get('status', 'N/A'),
                    'url_hinh_anh': anime.get('images', {}).get('jpg', {}).get('image_url', '')
                }
                for anime in duLieuAnime[:20]
            ]
            self.boNhoDemApi[khoaBoNhoDem] = animeDaXuLy
            tatCaAnime = []
            if os.path.exists('du_lieu_anime.json'):
                with open('du_lieu_anime.json', 'r') as f:
                    tatCaAnime = json.load(f)
            tieuDeHienCo = {anime['tieu_de'] for anime in tatCaAnime}
            tatCaAnime.extend(anime for anime in animeDaXuLy if anime['tieu_de'] not in tieuDeHienCo)
            with open('du_lieu_anime.json', 'w') as f:
                json.dump(tatCaAnime, f, indent=4)
            return animeDaXuLy
        except Exception as e:
            raise Exception(f"Không thể lấy dữ liệu anime: {str(e)}")

    def timKiemAnimeApi(self):
        truyVan = self.oNhapTimKiem.get()
        if not truyVan:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm")
            return

        def nhiemVuTimKiem():
            try:
                khoaBoNhoDem = f"tim_kiem_{truyVan}"
                if khoaBoNhoDem in self.boNhoDemApi:
                    return self.boNhoDemApi[khoaBoNhoDem]
                time.sleep(0.5)
                phanHoi = requests.get(f"https://api.jikan.moe/v4/anime", params={'q': truyVan})
                if phanHoi.status_code != 200:
                    raise Exception("Không thể lấy dữ liệu từ API")
                duLieuAnime = phanHoi.json()['data']
                if not duLieuAnime:
                    return []
                animeDaXuLy = [
                    {
                        'tieu_de': anime['title'],
                        'diem_so': str(anime.get('score', 'N/A')),
                        'so_tap': str(anime.get('episodes', 'N/A')),
                        'trang_thai': anime.get('status', 'N/A'),
                        'url_hinh_anh': anime.get('images', {}).get('jpg', {}).get('image_url', '')
                    }
                    for anime in duLieuAnime[:20]
                ]
                self.boNhoDemApi[khoaBoNhoDem] = animeDaXuLy
                tatCaAnime = []
                if os.path.exists('du_lieu_anime.json'):
                    with open('du_lieu_anime.json', 'r') as f:
                        tatCaAnime = json.load(f)
                tieuDeHienCo = {anime['tieu_de'] for anime in tatCaAnime}
                tatCaAnime.extend(anime for anime in animeDaXuLy if anime['tieu_de'] not in tieuDeHienCo)
                with open('du_lieu_anime.json', 'w') as f:
                    json.dump(tatCaAnime, f, indent=4)
                return animeDaXuLy
            except Exception as e:
                raise Exception(f"Không thể tìm kiếm anime: {str(e)}")

        threading.Thread(target=lambda: self.nhiemVuNen(nhiemVuTimKiem)).start()

    def sapXepAnime(self):
        khoaSapXep = self.bienSapXep.get().lower()
        if khoaSapXep == "tiêu đề":
            self.danhSachHienThiHienTai.sort(key=lambda x: x['tieu_de'])
        elif khoaSapXep == "điểm số":
            self.danhSachHienThiHienTai.sort(key=lambda x: float(x['diem_so']) if x['diem_so'] != 'N/A' else 0, reverse=True)
        elif khoaSapXep == "số tập":
            self.danhSachHienThiHienTai.sort(key=lambda x: int(x['so_tap']) if x['so_tap'] != 'N/A' else 0, reverse=True)
        self.hienThiLuoiAnime(self.danhSachHienThiHienTai)

    def thayDoiDiemSo(self, anime):
        cuaSoDiemSo = tk.Toplevel(self.cuaSo)
        cuaSoDiemSo.title(f"Thay đổi điểm số cho {anime['tieu_de']}")
        cuaSoDiemSo.geometry("300x150")
        ttk.Label(cuaSoDiemSo, text=f"Điểm số hiện tại: {anime['diem_so']}", font=('Arial', 12)).pack(pady=10)
        ttk.Label(cuaSoDiemSo, text="Nhập điểm số mới (0-10):").pack()
        oNhapDiemSo = ttk.Entry(cuaSoDiemSo)
        oNhapDiemSo.pack(pady=5)

        def capNhatDiemSo():
            diemSoMoi = oNhapDiemSo.get()
            try:
                diemSoMoi = float(diemSoMoi)
                if not 0 <= diemSoMoi <= 10:
                    messagebox.showerror("Lỗi", "Điểm số phải nằm trong khoảng từ 0 đến 10!")
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập một số hợp lệ!")
                return

            # Cập nhật điểm số trong danh sách hiện tại
            for a in self.danhSachHienThiHienTai:
                if a['tieu_de'] == anime['tieu_de']:
                    a['diem_so'] = str(diemSoMoi)
                    break

            # Cập nhật điểm số trong du_lieu_anime.json
            try:
                with open('du_lieu_anime.json', 'r') as f:
                    tatCaAnime = json.load(f)
                for a in tatCaAnime:
                    if a['tieu_de'] == anime['tieu_de']:
                        a['diem_so'] = str(diemSoMoi)
                        break
                with open('du_lieu_anime.json', 'w') as f:
                    json.dump(tatCaAnime, f, indent=4)
                messagebox.showinfo("Thành công", f"Đã cập nhật điểm số cho {anime['tieu_de']} thành {diemSoMoi}!")
                cuaSoDiemSo.destroy()
                self.hienThiLuoiAnime(self.danhSachHienThiHienTai)  # Làm mới giao diện
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật điểm số: {str(e)}")

        ttk.Button(cuaSoDiemSo, text="Cập nhật", command=capNhatDiemSo).pack(pady=10)

    def hienThiLuoiAnime(self, danhSachAnime):
        for widget in self.khungCoTheCuon.winfo_children():
            widget.destroy()
        if not danhSachAnime:
            ttk.Label(self.khungCoTheCuon, text="Không tìm thấy anime", style='TieuDe.TLabel', font=('Arial', 14)).pack(expand=True, pady=50)
            return

        soCotToiDa = 3
        for i in range(soCotToiDa):
            self.khungCoTheCuon.columnconfigure(i, weight=1, uniform='cot')
        hang, cot = 0, 0
        for anime in danhSachAnime:
            khungAnime = ttk.Frame(self.khungCoTheCuon, width=350)
            khungAnime.grid(row=hang, column=cot, padx=20, pady=20, sticky="nsew")
            khungAnime.grid_propagate(False)
            khungVien = ttk.Frame(khungAnime, style='The.TFrame')
            khungVien.pack(expand=True, fill='both', padx=10, pady=10)

            boChuaHinhAnh = ttk.Frame(khungVien, width=200, height=300)
            boChuaHinhAnh.pack(pady=10)
            boChuaHinhAnh.pack_propagate(False)
            urlHinhAnh = anime.get('url_hinh_anh', '')
            if urlHinhAnh:
                ttk.Label(boChuaHinhAnh, text="Đang tải...").place(relx=0.5, rely=0.5, anchor='center')
                threading.Thread(target=self.taiHinhAnhKhongDongBo, args=(boChuaHinhAnh, urlHinhAnh)).start()
            else:
                ttk.Label(boChuaHinhAnh, text="Hình ảnh không có sẵn").place(relx=0.5, rely=0.5, anchor='center')

            ttk.Label(khungVien, text=anime['tieu_de'], wraplength=280, style='TieuDe.TLabel', justify='center').pack(pady=(10, 5))
            khungThongTin = ttk.Frame(khungVien)
            khungThongTin.pack(pady=10, fill='x')
            ttk.Label(khungThongTin, text="Điểm số: ", style='TieuDe.TLabel').pack(side='left', padx=25)
            ttk.Label(khungThongTin, text=anime.get('diem_so', 'N/A')).pack(side='left', padx=(0, 15))
            ttk.Label(khungThongTin, text="Số tập: ", style='TieuDe.TLabel').pack(side='left', padx=5)
            ttk.Label(khungThongTin, text=anime.get('so_tap', 'N/A')).pack(side='left')

            khungNut = ttk.Frame(khungVien)
            khungNut.pack(pady=5)
            laYeuThich = anime['tieu_de'] in self.danhSachYeuThichNguoiDungHienTai
            tk.Button(khungNut, text="♥" if laYeuThich else "♡", command=lambda a=anime: self.batTatYeuThich(a),
                      relief="flat", font=("Arial", 12), fg="red" if laYeuThich else "gray", bg="white", width=2, height=1).pack(side='left', padx=5)
            if self.vaiTroHienTai == "admin":
                ttk.Button(khungNut, text="Thay đổi điểm số", command=lambda a=anime: self.thayDoiDiemSo(a)).pack(side='left', padx=5)

            cot += 1
            if cot >= soCotToiDa:
                cot = 0
                hang += 1

    def taiHinhAnhKhongDongBo(self, boChua, url):
        anh = self.layHinhAnh(url)
        if anh:
            self.cuaSo.after(0, lambda: self.capNhatHinhAnh(boChua, anh))

    def capNhatHinhAnh(self, boChua, anh):
        for widget in boChua.winfo_children():
            widget.destroy()
        nhanHinhAnh = ttk.Label(boChua, image=anh)
        nhanHinhAnh.image = anh
        nhanHinhAnh.place(relx=0.5, rely=0.5, anchor='center')

    def batTatYeuThich(self, anime):
        try:
            with open('nguoi_dung.json', 'r') as f:
                nguoiDung = json.load(f)
            if 'yeu_thich' not in nguoiDung[self.nguoiDungHienTai]:
                nguoiDung[self.nguoiDungHienTai]['yeu_thich'] = []
            yeuThich = nguoiDung[self.nguoiDungHienTai]['yeu_thich']
            if anime['tieu_de'] in yeuThich:
                yeuThich.remove(anime['tieu_de'])
            else:
                yeuThich.append(anime['tieu_de'])
            with open('nguoi_dung.json', 'w') as f:
                json.dump(nguoiDung, f, indent=4)
            self.danhSachYeuThichNguoiDungHienTai = yeuThich
            if getattr(self, 'laCheDoYeuThich', False):
                self.hienThiYeuThich()
            else:
                self.hienThiLuoiAnime(self.danhSachHienThiHienTai)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật danh sách yêu thích: {str(e)}")

    def hienThiYeuThich(self):
        try:
            with open('nguoi_dung.json', 'r') as f:
                nguoiDung = json.load(f)
            self.danhSachYeuThichNguoiDungHienTai = nguoiDung[self.nguoiDungHienTai].get('yeu_thich', [])
            if not os.path.exists('du_lieu_anime.json'):
                messagebox.showinfo("Thông báo", "Không có dữ liệu anime. Vui lòng làm mới danh sách trước.")
                self.hienThiLuoiAnime([])
                return
            with open('du_lieu_anime.json', 'r') as f:
                tatCaAnime = json.load(f)
            animeYeuThich = [anime for anime in tatCaAnime if anime['tieu_de'] in self.danhSachYeuThichNguoiDungHienTai]
            if not animeYeuThich:
                messagebox.showinfo("Thông báo", "Danh sách yêu thích của bạn hiện đang trống hoặc các anime yêu thích không có trong dữ liệu hiện tại.")
            self.laCheDoYeuThich = True
            self.hienThiLuoiAnime(animeYeuThich)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách yêu thích: {str(e)}")

    def chuyenSangCheDoTatCa(self):
        self.laCheDoYeuThich = False
        self.hienThiLuoiAnime(self.danhSachHienThiHienTai)

    def chay(self):
        kieu = ttk.Style()
        kieu.configure('The.TFrame', relief='solid', borderwidth=1)
        kieu.configure('Tai.TFrame', background='white')
        self.cuaSo.option_add('*TLabel.font', ('Arial', 10))
        kieu.configure('TieuDe.TLabel', font=('Arial', 12, 'bold'))
        self.cuaSo.mainloop()

if __name__ == "__main__":
    ungDung = QuanLyAnime()
    ungDung.chay()