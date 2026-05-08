import sys
import os
import sqlite3
import hashlib
import shutil
import uuid
import gc
from PIL import Image
from typing import cast

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QStackedWidget, QGridLayout, 
    QScrollArea, QFrame, QDoubleSpinBox, QSpinBox, QComboBox, 
    QTextEdit, QMessageBox, QGraphicsOpacityEffect, QFileDialog, QGraphicsEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, QAbstractAnimation, QTimer
from PySide6.QtGui import QPixmap, QCursor, QDragEnterEvent, QDropEvent

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)

    if "Content/MacOS" in BASE_DIR:
        BASE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../.."))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")
DB_PATH = os.path.join(DATA_DIR, "dossiers.db")

os.makedirs(PHOTOS_DIR, exist_ok=True)

STYLESHEET = """
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px;
    color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid #007acc;
}
QPushButton {
    background-color: #007acc;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0098ff;
}
QPushButton:pressed {
    background-color: #005f9e;
}
QPushButton#secondaryBtn {
    background-color: #3d3d3d;
}
QPushButton#secondaryBtn:hover {
    background-color: #4d4d4d;
}
QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #3d3d3d;
    border-radius: 5px;
}
"""

# ==========================================
# DATABASE MANAGER (Model)
# ==========================================
class DatabaseManager:
    """Управляет всеми взаимодействиями с SQLite."""
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Таблица пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)
            # Таблица досье
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dossiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    last_name TEXT,
                    nicknames TEXT,
                    age INTEGER,
                    weight REAL,
                    shoe_size TEXT,
                    skin_color TEXT,
                    comments TEXT,
                    photo_path TEXT,
                    FOREIGN KEY(creator_id) REFERENCES users(id)
                )
            """)
            conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username, password):
        # Если пользователь найден - проверяет пароль. 
        # Если не найден - создает нового.
        # Возвращает ID пользователя или None (если неверный пароль).
        pwd_hash = self.hash_password(password)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if user:
                if user[1] == pwd_hash:
                    return user[0]
                else:
                    return None
            else:
                # Создаем нового пользователя
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
                conn.commit()
                return cursor.lastrowid

    def save_dossier(self, dossier_data):
        # Создает или обновляет досье.
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if dossier_data.get('id'):
                cursor.execute("""
                    UPDATE dossiers SET 
                    name=?, last_name=?, nicknames=?, age=?, weight=?, shoe_size=?, skin_color=?, comments=?, photo_path=?
                    WHERE id=? AND creator_id=?
                """, (
                    dossier_data['name'], dossier_data['last_name'], dossier_data['nicknames'],
                    dossier_data['age'], dossier_data['weight'], dossier_data['shoe_size'],
                    dossier_data['skin_color'], dossier_data['comments'], dossier_data['photo_path'],
                    dossier_data['id'], dossier_data['creator_id']
                ))
                return dossier_data['id']
            else:
                # Создание
                cursor.execute("""
                    INSERT INTO dossiers 
                    (creator_id, name, last_name, nicknames, age, weight, shoe_size, skin_color, comments, photo_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    dossier_data['creator_id'], dossier_data['name'], dossier_data['last_name'], dossier_data['nicknames'],
                    dossier_data['age'], dossier_data['weight'], dossier_data['shoe_size'],
                    dossier_data['skin_color'], dossier_data['comments'], dossier_data['photo_path']
                ))
                return cursor.lastrowid

    def get_dossiers(self, search_query=""):
        # Получает список досье для Dashboard.
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = """
                SELECT d.id, d.name, d.last_name, d.photo_path, u.username as author_name 
                FROM dossiers d
                JOIN users u ON d.creator_id = u.id
            """
            params = []
            if search_query:
                query += " WHERE d.name LIKE ? OR d.last_name LIKE ? OR d.nicknames LIKE ?"
                search_term = f"%{search_query}%"
                params = [search_term, search_term, search_term]
                
            query += " ORDER BY d.id DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_dossier(self, dossier_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dossiers WHERE id = ?", (dossier_id,))
            row = cursor.fetchone()
            return dict(row) if row else None


# ==========================================
# IMAGE PROCESSOR
# ==========================================
class ImageProcessor:
    MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB
    MAX_DIMENSION = 4096              # px
    ALLOWED_FORMATS = ['JPEG', 'PNG', 'WEBP', 'MPO']

    @classmethod
    def validate_image(cls, file_path):
        try:
            size = os.path.getsize(file_path)
            if size > cls.MAX_SIZE_BYTES:
                return False, "Файл превышает допустимый размер в 5 МБ."

            with Image.open(file_path) as img:
                w, h = img.size
                if w > cls.MAX_DIMENSION or h > cls.MAX_DIMENSION:
                    return False, f"Разрешение превышает {cls.MAX_DIMENSION}px по одной из сторон."
                
                if img.format not in cls.ALLOWED_FORMATS:
                    return False, f"Неподдерживаемый формат: {img.format}. Разрешены JPG, PNG, WEBP."
                
            return True, ""
        except Exception as e:
            return False, f"Ошибка чтения файла: {str(e)}"

    @classmethod
    def process_and_save(cls, file_path):
        # Сохраняет оригинал и создает миниатюру для оптимизации памяти сетки.
        ext = os.path.splitext(file_path)[1].lower()
        if not ext or ext == '.mpo': ext = '.jpg'
        
        base_filename = str(uuid.uuid4())
        new_filename = f"{base_filename}{ext}"
        thumb_filename = f"{base_filename}_thumb.jpg"
        
        dest_path = os.path.join(PHOTOS_DIR, new_filename)
        thumb_path = os.path.join(PHOTOS_DIR, thumb_filename)

        # Копируем оригинал
        shutil.copy2(file_path, dest_path)

        # Создаем миниатюру
        with Image.open(file_path) as img:
            img.thumbnail((256, 256))
            if img.mode in ("RGBA", "P"): 
                img = img.convert("RGB")
            img.save(thumb_path, "JPEG", quality=85)

        return new_filename


# ==========================================
# UI COMPONENTS
# ==========================================

class PhotoDropArea(QLabel):
    photo_dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Перетащите фото сюда\nили нажмите для выбора\n(Макс. 5МБ, 4096px)")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 8px;
                background-color: #2a2a2a;
                color: #888888;
            }
            QLabel:hover {
                border-color: #007acc;
                background-color: #2d333b;
            }
        """)
        self.setFixedSize(250, 300)
        self.setAcceptDrops(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.current_photo_path = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("border: 2px dashed #007acc; background-color: #2d333b; color: #ffffff;")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 8px;
                background-color: #2a2a2a;
                color: #888888;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        self.dragLeaveEvent(None) # reset style
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.handle_file(file_path)

    def mousePressEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if file_path:
            self.handle_file(file_path)

    def handle_file(self, file_path):
        is_valid, error_msg = ImageProcessor.validate_image(file_path)
        if is_valid:
            self.set_image(file_path)
            self.photo_dropped.emit(file_path)
        else:
            QMessageBox.warning(self, "Ошибка загрузки", error_msg)

    def set_image(self, file_path):
        self.current_photo_path = file_path
        if file_path:
            pixmap = QPixmap(file_path)
            self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        else:
            self.clear()
            self.setText("Перетащите фото сюда")

    def cleanup(self):
        self.clear()
        self.current_photo_path = None


class FloatingButton(QPushButton):
    def __init__(self, parent):
        super().__init__("+", parent)
        self.setFixedSize(60, 60)
        self.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border-radius: 30px;
                font-size: 32px;
                font-weight: bold;
                padding-bottom: 4px;
            }
            QPushButton:hover { background-color: #0098ff; }
            QPushButton:pressed { background-color: #005f9e; }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class DossierCard(QFrame):
    clicked = Signal(int)

    def __init__(self, dossier_data):
        super().__init__()
        self.dossier_id = dossier_data['id']
        self.setFixedSize(200, 260)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
            }
            QFrame:hover {
                background-color: #353535;
                border: 1px solid #007acc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Thumbnail
        self.img_label = QLabel()
        self.img_label.setFixedSize(180, 180)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setStyleSheet("background-color: #1e1e1e; border-radius: 4px;")
        
        photo_path = dossier_data.get('photo_path')
        if photo_path:
            thumb_name = photo_path.replace('.', '_thumb.')
            full_path = os.path.join(PHOTOS_DIR, thumb_name)
            if not os.path.exists(full_path): 
                full_path = os.path.join(PHOTOS_DIR, photo_path) # Fallback
            
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path)
                self.img_label.setPixmap(pixmap.scaled(self.img_label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        
        layout.addWidget(self.img_label)

        # Name
        name_label = QLabel(f"{dossier_data['name']} {dossier_data.get('last_name', '')}")
        name_label.setStyleSheet("font-weight: bold; font-size: 16px; border: none;")
        layout.addWidget(name_label)

        # Author
        author_label = QLabel(f"Автор: {dossier_data['author_name']}")
        author_label.setStyleSheet("color: #888888; font-size: 12px; border: none;")
        layout.addWidget(author_label)

    def mousePressEvent(self, event):
        self.clicked.emit(self.dossier_id)

    def cleanup(self):
        self.img_label.clear()


# ==========================================
# SCREENS (VIEWS)
# ==========================================

class AuthWidget(QWidget):
    login_success = Signal(int)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(350, 400)
        container.setStyleSheet("background-color: #252526; border-radius: 10px;")
        
        form_layout = QVBoxLayout(container)
        form_layout.setContentsMargins(30, 40, 30, 40)
        form_layout.setSpacing(15)

        title = QLabel("Досье")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        form_layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Имя пользователя")
        form_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_input)

        info = QLabel("Если аккаунта нет, он будет создан автоматически.")
        info.setStyleSheet("color: #888; font-size: 11px;")
        info.setWordWrap(True)
        form_layout.addWidget(info)

        login_btn = QPushButton("Вход / Регистрация")
        login_btn.clicked.connect(self._handle_login)
        form_layout.addWidget(login_btn)

        layout.addWidget(container)

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        user_id = self.db_manager.authenticate(username, password)
        if user_id:
            self.login_success.emit(user_id)
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный пароль для существующего пользователя")


class DashboardWidget(QWidget):
    open_dossier = Signal(int)
    create_dossier = Signal()
    logout = Signal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.cards = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени или прозвищу...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.load_data)

        logout_btn = QPushButton("Выйти")
        logout_btn.setObjectName("secondaryBtn")
        logout_btn.clicked.connect(self.logout.emit)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(logout_btn)
        layout.addLayout(header_layout)

        # Grid Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background-color: transparent;")
        
        # Мы используем FlowLayout-подобное поведение с помощью вычислений в resizeEvent
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_area.setWidget(self.grid_container)
        layout.addWidget(self.scroll_area)

        # Floating Action Button
        self.fab = FloatingButton(self)
        self.fab.clicked.connect(self.create_dossier.emit)

    def load_data(self):
        self._clear_grid()
        
        query = self.search_input.text().strip()
        dossiers = self.db_manager.get_dossiers(query)

        for i, data in enumerate(dossiers):
            card = DossierCard(data)
            card.clicked.connect(self.open_dossier.emit)
            self.cards.append(card)
            
            # Анимация появления карточки (Fade In)
            eff = QGraphicsOpacityEffect(card)
            card.setGraphicsEffect(eff)
            anim = QPropertyAnimation(eff, b"opacity")
            anim.setDuration(400)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            QTimer.singleShot(i * 50, lambda a = anim:
            a.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped))

        self.reflow_grid()

    def _clear_grid(self):
        for card in self.cards:
            self.grid_layout.removeWidget(card)
            card.cleanup()
            card.deleteLater()
        self.cards.clear()
        gc.collect()

    def reflow_grid(self):
        if not self.cards:
            return
        
        width = self.scroll_area.width()
        col_width = 220
        cols = max(1, width // col_width)

        for i, card in enumerate(self.cards):
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(card, row, col)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fab.move(self.width() - self.fab.width() - 30, self.height() - self.fab.height() - 30)
        self.reflow_grid()


class DossierFormWidget(QWidget):
    back_to_dashboard = Signal()
    save_success = Signal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_user_id = None
        self.dossier_id = None
        self.is_read_only = False
        self.original_photo = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton("← Назад")
        back_btn.setObjectName("secondaryBtn")
        back_btn.clicked.connect(self._on_back_clicked)
        
        self.title_label = QLabel("Создание досье")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.save_btn = QPushButton("Опубликовать / Сохранить")
        self.save_btn.clicked.connect(self.save_data)

        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.save_btn)
        layout.addLayout(header)

        # Main Content
        content = QHBoxLayout()
        
        # Left Side: Photo
        photo_layout = QVBoxLayout()
        self.photo_area = PhotoDropArea()
        photo_layout.addWidget(self.photo_area)
        photo_layout.addStretch()
        content.addLayout(photo_layout)

        # Right Side: Form Fields
        form_layout = QGridLayout()
        form_layout.setSpacing(15)

        self.name_in = QLineEdit(); self.name_in.setPlaceholderText("Обязательно")
        self.last_name_in = QLineEdit()
        self.nicknames_in = QLineEdit()
        
        self.age_in = QSpinBox()
        self.age_in.setRange(0, 150)
        
        self.weight_in = QDoubleSpinBox()
        self.weight_in.setRange(0.0, 500.0)
        self.weight_in.setSuffix(" кг")

        self.shoe_size_in = QComboBox()
        self.shoe_size_in.addItems(["Неизвестно", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46+"])

        self.skin_color_in = QComboBox()
        self.skin_color_in.addItems(["Неизвестно", "Светлый", "Загорелый", "Темный", "Оливковый", "Другой"])

        # Row 0
        form_layout.addWidget(QLabel("Имя:*"), 0, 0)
        form_layout.addWidget(self.name_in, 0, 1)
        form_layout.addWidget(QLabel("Фамилия:"), 0, 2)
        form_layout.addWidget(self.last_name_in, 0, 3)

        # Row 1
        form_layout.addWidget(QLabel("Прозвища:"), 1, 0)
        form_layout.addWidget(self.nicknames_in, 1, 1, 1, 3)

        # Row 2
        form_layout.addWidget(QLabel("Возраст:"), 2, 0)
        form_layout.addWidget(self.age_in, 2, 1)
        form_layout.addWidget(QLabel("Вес:"), 2, 2)
        form_layout.addWidget(self.weight_in, 2, 3)

        # Row 3
        form_layout.addWidget(QLabel("Размер ноги:"), 3, 0)
        form_layout.addWidget(self.shoe_size_in, 3, 1)
        form_layout.addWidget(QLabel("Цвет кожи:"), 3, 2)
        form_layout.addWidget(self.skin_color_in, 3, 3)

        content.addLayout(form_layout)
        content.setStretch(1, 1) # Form takes more space
        layout.addLayout(content)

        # Bottom: Comments
        layout.addWidget(QLabel("Комментарии и особые приметы:"))
        self.comments_in = QTextEdit()
        layout.addWidget(self.comments_in)

    def setup_mode(self, user_id, dossier_id=None):
        self.current_user_id = user_id
        self.dossier_id = dossier_id
        self.original_photo = None
        self.photo_area.current_photo_path = None
        
        # Сброс полей
        self.name_in.clear()
        self.last_name_in.clear()
        self.nicknames_in.clear()
        self.age_in.setValue(0)
        self.weight_in.setValue(0.0)
        self.shoe_size_in.setCurrentIndex(0)
        self.skin_color_in.setCurrentIndex(0)
        self.comments_in.clear()
        self.photo_area.clear()
        self.photo_area.setText("Перетащите фото сюда\nили нажмите для выбора\n(Макс. 5МБ, 4096px)")

        if dossier_id:
            # Режим просмотра / редактирования
            data = self.db_manager.get_dossier(dossier_id)
            if not data: return
            
            self.title_label.setText(f"Досье: {data['name']}")
            self.name_in.setText(data['name'])
            self.last_name_in.setText(data['last_name'] or "")
            self.nicknames_in.setText(data['nicknames'] or "")
            self.age_in.setValue(data['age'] or 0)
            self.weight_in.setValue(data['weight'] or 0.0)
            self.shoe_size_in.setCurrentText(data['shoe_size'] or "Неизвестно")
            self.skin_color_in.setCurrentText(data['skin_color'] or "Неизвестно")
            self.comments_in.setText(data['comments'] or "")
            
            self.original_photo = data['photo_path']
            if self.original_photo:
                full_path = os.path.join(PHOTOS_DIR, self.original_photo)
                if os.path.exists(full_path):
                    self.photo_area.set_image(full_path)

            self.is_read_only = data['creator_id'] != self.current_user_id
        else:
            # Режим создания
            self.title_label.setText("Новое досье")
            self.is_read_only = False

        self._apply_permissions()

    def _apply_permissions(self):
        widgets = [self.name_in, self.last_name_in, self.nicknames_in, self.age_in, 
                   self.weight_in, self.shoe_size_in, self.skin_color_in, self.comments_in]
        
        for w in widgets:
            w.setEnabled(not self.is_read_only)
        
        self.photo_area.setAcceptDrops(not self.is_read_only)
        self.photo_area.setEnabled(not self.is_read_only)
        
        if self.is_read_only:
            self.save_btn.hide()
        else:
            self.save_btn.show()

    def save_data(self):
        name = self.name_in.text().strip()
        if not name:
            QMessageBox.warning(self, "Внимание", "Поле 'Имя' обязательно для заполнения.")
            return

        # Обработка фото
        photo_filename = self.original_photo
        new_photo_path = self.photo_area.current_photo_path
        
        # Если было выбрано новое фото, отличное от того что в БД
        if new_photo_path and not new_photo_path.startswith(PHOTOS_DIR):
            try:
                photo_filename = ImageProcessor.process_and_save(new_photo_path)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения фото", str(e))
                return

        data = {
            'id': self.dossier_id,
            'creator_id': self.current_user_id,
            'name': name,
            'last_name': self.last_name_in.text().strip(),
            'nicknames': self.nicknames_in.text().strip(),
            'age': self.age_in.value(),
            'weight': self.weight_in.value(),
            'shoe_size': self.shoe_size_in.currentText(),
            'skin_color': self.skin_color_in.currentText(),
            'comments': self.comments_in.toPlainText().strip(),
            'photo_path': photo_filename
        }

        self.db_manager.save_dossier(data)
        self.save_success.emit()

    def _on_back_clicked(self):
        self.cleanup_memory()
        self.back_to_dashboard.emit()

    def cleanup_memory(self):
        self.photo_area.cleanup()
        # Сброс остальных текстовых полей, чтобы не держать в памяти большие комментарии
        self.comments_in.clear()


# ==========================================
# MAIN APPLICATION CONTROLLER
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dossier Management System")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(STYLESHEET)

        self.db_manager = DatabaseManager(DB_PATH)
        self.current_user_id = None

        # Инициализация экранов
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.auth_view = AuthWidget(self.db_manager)
        self.dash_view = DashboardWidget(self.db_manager)
        self.form_view = DossierFormWidget(self.db_manager)

        self.stacked_widget.addWidget(self.auth_view)  # index 0
        self.stacked_widget.addWidget(self.dash_view)  # index 1
        self.stacked_widget.addWidget(self.form_view)  # index 2

        self._connect_signals()
        
        # Начинаем с экрана входа
        self.stacked_widget.setCurrentIndex(0)

    def _connect_signals(self):
        # Сигналы авторизации
        self.auth_view.login_success.connect(self._on_login_success)
        
        # Сигналы Dashboard
        self.dash_view.logout.connect(self._on_logout)
        self.dash_view.create_dossier.connect(self._on_create_dossier)
        self.dash_view.open_dossier.connect(self._on_open_dossier)
        
        # Сигналы Формы
        self.form_view.back_to_dashboard.connect(self._show_dashboard)
        self.form_view.save_success.connect(self._on_save_success)

    def _animate_transition(self, next_index):
        current_widget = self.stacked_widget.currentWidget()
        next_widget = self.stacked_widget.widget(next_index)

        # Проверка для Pylance: если виджеты не найдены, просто переключаем индекс без анимации
        if not current_widget or not next_widget:
            self.stacked_widget.setCurrentIndex(next_index)
            return

        # Настраиваем эффекты
        eff_out = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(eff_out)
        
        eff_in = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(eff_in)

        # Анимация затухания текущего экрана
        self.anim_out = QPropertyAnimation(eff_out, b"opacity")
        self.anim_out.setDuration(200)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)

        # Анимация появления следующего экрана
        self.anim_in = QPropertyAnimation(eff_in, b"opacity")
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)

        # По завершению fade-out переключаем индекс и запускаем fade-in
        def on_fade_out_finished():
            self.stacked_widget.setCurrentIndex(next_index)
            # Убираем эффект с предыдущего, чтобы не мешал кликам
            # Проверка is_empty для безопасности во время закрытия приложения
            if current_widget:
                current_widget.setGraphicsEffect(cast(QGraphicsEffect, None))
            self.anim_in.start()

        self.anim_out.finished.connect(on_fade_out_finished)
        self.anim_out.start()

    def _on_login_success(self, user_id):
        self.current_user_id = user_id
        self._show_dashboard()

    def _on_logout(self):
        self.current_user_id = None
        self.dash_view._clear_grid() # Очищаем память и данные других пользователей
        self._animate_transition(0)

    def _show_dashboard(self):
        self.dash_view.load_data()
        self._animate_transition(1)

    def _on_create_dossier(self):
        self.form_view.setup_mode(self.current_user_id)
        self._animate_transition(2)

    def _on_open_dossier(self, dossier_id):
        self.form_view.setup_mode(self.current_user_id, dossier_id)
        self._animate_transition(2)

    def _on_save_success(self):
        # После сохранения очищаем память формы и возвращаемся в Dashboard
        self.form_view.cleanup_memory()
        self._show_dashboard()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())