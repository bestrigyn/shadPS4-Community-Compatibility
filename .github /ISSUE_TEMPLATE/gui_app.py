import sys, os, requests, re, json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,  
                             QScrollArea, QGridLayout, QFrame, QPushButton,
                             QLineEdit, QHBoxLayout, QMenu, QMessageBox, QComboBox, QCheckBox, QTextEdit)
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import Qt

APP_TITLE = 'shadPS4 Explorer v1.0.1'
GITHUB_API = "https://api.github.com/repos/bestrigyn/shadPS4-Community-Compatibility/issues?per_page=100"
CACHE_FILE = "local_database.json"


def clean_body_text(text):
    if not text: return "No data available."
    text = re.sub(r'<img.*?>|\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'(?s).*?###\s*4\s*Platform', '### Platform', text)
    return text.strip()


class ReportWindow(QWidget):
    """Окно создания отчета (копия твоего скриншота)"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("COMPATIBILITY REPORT FORM")
        self.resize(500, 600)
        self.setStyleSheet("background-color: #1a1a1a; color: white; font-family: 'Segoe UI';")

        lay = QVBoxLayout(self)

        title = QLabel("COMPATIBILITY REPORT FORM")
        title.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        lay.addWidget(QCheckBox("I understand this is a Community list and all data types are accepted *"))

        lay.addWidget(QLabel("4. Copy Type (Select one): *"))
        copy_lay = QHBoxLayout()
        copy_lay.addWidget(QCheckBox("Pirated (Downloaded)"))
        copy_lay.addWidget(QCheckBox("Digital Dump (Own)"))
        lay.addLayout(copy_lay)

        lay.addWidget(QLabel("1. Game Name:"))
        lay.addWidget(QLineEdit())

        lay.addWidget(QLabel("2. Game ID (CUSA):"))
        lay.addWidget(QLineEdit("CUSA"))

        lay.addWidget(QLabel("5. shadPS4 Version:"))
        ver_box = QComboBox()
        ver_box.addItems(["v0.1", "v0.5", "v0.6", "v0.7", "v0.8", "v0.10", "v0.13"])
        lay.addWidget(ver_box)

        lay.addWidget(QLabel("6. Status:"))
        stat_box = QComboBox()
        stat_box.addItems(["Nothing", "Bootable", "Intro", "Menu", "In-Game", "Playable"])
        lay.addWidget(stat_box)

        lay.addWidget(QLabel("7. Error Summary:"))
        lay.addWidget(QTextEdit())

        send_btn = QPushButton("GENERATE & SEND")
        send_btn.setStyleSheet(
            "background: #0078d7; color: white; font-weight: bold; padding: 15px; margin-top: 10px; border: none;")
        send_btn.clicked.connect(
            lambda: QMessageBox.information(self, "Success", "Report generated! (Sending logic is coming soon)"))
        lay.addWidget(send_btn)


class InfoWindow(QWidget):
    def __init__(self, title, content):
        super().__init__()
        self.setWindowTitle(f"Full Info - {title}")
        self.resize(700, 550)
        self.setStyleSheet("background-color: #0a0a0a; color: #00ff00; border: 1px solid #0078d7;")
        lay = QVBoxLayout(self)
        header = QLabel(f"GAME: {title}")
        header.setStyleSheet("font-weight: bold; font-size: 16pt; color: white; border: none; padding: 10px;")
        lay.addWidget(header)
        self.txt = QLabel(content)
        self.txt.setWordWrap(True)
        self.txt.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.txt.setStyleSheet(
            "color: #00ff00; background: #050505; font-family: 'Consolas'; font-size: 12pt; padding: 15px;")
        scroll = QScrollArea();
        scroll.setWidgetResizable(True);
        scroll.setWidget(self.txt)
        lay.addWidget(scroll)
        btn = QPushButton("CLOSE");
        btn.clicked.connect(self.close)
        btn.setStyleSheet("background: #333; color: white; padding: 12px; font-weight: bold; border: none;")
        lay.addWidget(btn)


class GameCard(QFrame):
    def __init__(self, game_data):
        super().__init__()
        self.game = game_data
        self.setFixedSize(220, 270)
        self.setStyleSheet("background: #0a0a0a; border: 1px solid #222; border-radius: 8px;")
        lay = QVBoxLayout(self)
        self.img_lbl = QLabel();
        self.img_lbl.setFixedSize(200, 180);
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_image(self.game.get('img', ''))
        lay.addWidget(self.img_lbl)
        t_lbl = QLabel(self.game.get('title', 'Unknown'))
        t_lbl.setWordWrap(True);
        t_lbl.setStyleSheet("font-size: 11px; color: #0078d7; border: none; font-weight: bold;")
        lay.addWidget(t_lbl)

    def load_image(self, url):
        if not url: return
        try:
            r = requests.get(url, timeout=3)
            pix = QPixmap();
            pix.loadFromData(r.content)
            self.img_lbl.setPixmap(
                pix.scaled(200, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except:
            self.img_lbl.setText("NO IMAGE")

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("background-color: #111; color: white; border: 1px solid #0078d7;")
        info_action = QAction("📋 Show Info", self)
        info_action.triggered.connect(self.open_info)
        menu.addAction(info_action)
        menu.exec(event.globalPos())

    def open_info(self):
        content = self.game.get('full_text', "No details found.")
        self.info = InfoWindow(self.game.get('title', ''), content)
        self.info.show()


class ShadExplorerV1(QWidget):
    def __init__(self):
        super().__init__()
        self.all_games = []
        self.initUI()
        self.load_cache()

    def initUI(self):
        self.setWindowTitle(APP_TITLE)
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #050505; color: white;")
        main_lay = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search game... (Right Click for Info)")
        self.search.setStyleSheet(
            "background: #111; border: 1px solid #333; padding: 12px; color: #0078d7; font-size: 14px;")
        self.search.textChanged.connect(self.run_search)

        sync_btn = QPushButton("🔄 SYNC")
        sync_btn.clicked.connect(self.sync_data)
        sync_btn.setStyleSheet("background: #111; border: 1px solid #28a745; padding: 12px; font-weight: bold;")

        report_btn = QPushButton("+ REPORT")
        report_btn.clicked.connect(self.open_report)
        report_btn.setStyleSheet("background: #111; border: 1px solid #0078d7; padding: 12px; font-weight: bold;")

        top_bar.addWidget(self.search)
        top_bar.addWidget(sync_btn)
        top_bar.addWidget(report_btn)
        main_lay.addLayout(top_bar)

        self.scroll = QScrollArea();
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget();
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        main_lay.addWidget(self.scroll)

    def open_report(self):
        self.rep = ReportWindow()
        self.rep.show()

    def load_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    self.all_games = json.load(f)
                self.draw_cards(self.all_games)
            except:
                pass

    def sync_data(self):
        try:
            r = requests.get(GITHUB_API, timeout=10)
            if r.status_code == 200:
                issues = r.json();
                new_data = []
                for iss in issues:
                    body = iss.get('body', '')
                    img = re.search(r'<img.*?src="(.*?)"', body)
                    new_data.append({"title": iss.get('title', 'Unknown'), "img": img.group(1) if img else "",
                                     "full_text": clean_body_text(body)})
                self.all_games = new_data
                with open(CACHE_FILE, 'w') as f:
                    json.dump(self.all_games, f)
                self.draw_cards(self.all_games)
                QMessageBox.information(self, "Done", "Database synchronized!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def draw_cards(self, data):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for i, game in enumerate(data): self.grid.addWidget(GameCard(game), i // 5, i % 5)

    def run_search(self):
        q = self.search.text().lower()
        filtered = [g for g in self.all_games if q in g['title'].lower()]
        self.draw_cards(filtered)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShadExplorerV1()
    window.show()
    sys.exit(app.exec())
