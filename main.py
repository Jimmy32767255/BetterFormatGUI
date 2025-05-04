import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QCheckBox, QSpinBox, QTextEdit,
                            QMessageBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt
import subprocess
import win32api
import json
import os

class BetterFormatGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BetterFormatGUI")
        self.setGeometry(100, 100, 400, 600)
        
        # 主控件
        self.main_widget = QWidget()
        
        # 创建滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.main_widget)
        self.setCentralWidget(self.scroll)
        
        # 主布局
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        # 加载预设
        self.presets_data = self.load_presets()
        
        # 创建UI
        self.create_drive_selection()
        self.create_format_options()
        self.create_presets()
        self.create_action_buttons()
        
    def create_drive_selection(self):
        """创建驱动器选择部分"""
        group = QGroupBox("选择驱动器")
        layout = QHBoxLayout()
        
        self.drive_combo = QComboBox()
        self.refresh_drives()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_drives)
        
        layout.addWidget(QLabel("驱动器:"))
        layout.addWidget(self.drive_combo)
        layout.addWidget(refresh_btn)
        layout.addStretch()
        
        group.setLayout(layout)
        self.main_layout.addWidget(group)
    
    def refresh_drives(self):
        """刷新可用驱动器列表"""
        self.drive_combo.clear()
        try:
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1] # Split by null character and remove last empty string
            formatted_drives = [d.replace('\\', '') for d in drives] # Format C:\ to C:
            self.drive_combo.addItems(formatted_drives)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法获取驱动器列表: {str(e)}")
    
    def create_format_options(self):
        """创建格式化选项部分"""
        group = QGroupBox("格式化选项")
        layout = QVBoxLayout()
        
        # 文件系统
        fs_layout = QHBoxLayout()
        fs_layout.addWidget(QLabel("文件系统:"))
        self.fs_combo = QComboBox()
        self.fs_combo.addItems(["FAT", "FAT32", "exFAT", "NTFS", "UDF", "ReFS"])
        fs_layout.addWidget(self.fs_combo)
        fs_layout.addStretch()
        layout.addLayout(fs_layout)
        
        # 卷标
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("卷标:"))
        self.volume_label = QLineEdit()
        label_layout.addWidget(self.volume_label)
        label_layout.addStretch()
        layout.addLayout(label_layout)
        
        group.setLayout(layout)
        self.main_layout.addWidget(group)

        # 分配单元大小
        cluster_layout = QHBoxLayout()
        cluster_layout.addWidget(QLabel("分配单元大小:"))
        self.cluster_combo = QComboBox()
        self.cluster_combo.addItems(["默认", "512", "1024", "2048", "4096", "8192", "16k", "32k", "64k", "128k", "256k", "512k", "1M", "2M", "4M", "8M", "16M", "32M"])
        cluster_layout.addWidget(self.cluster_combo)
        cluster_layout.addStretch()
        layout.addLayout(cluster_layout)
        
        # 快速格式化
        self.quick_format = QCheckBox("快速格式化")
        self.quick_format.setChecked(True)
        layout.addWidget(self.quick_format)
        
        # 压缩
        self.enable_compression = QCheckBox("启用文件和文件夹压缩")
        layout.addWidget(self.enable_compression)
        
        # 强制卸除卷
        self.Force_volume_disassembly = QCheckBox("强制卸除卷")
        layout.addWidget(self.Force_volume_disassembly)
        
        # UDF 版本
        udf_layout = QHBoxLayout()
        udf_layout.addWidget(QLabel("UDF 版本:"))
        self.UDFVersion = QComboBox()
        self.UDFVersion.addItems(["1.02", "1.50", "2.00", "2.01", "2.50"])
        self.UDFVersion.setCurrentText("2.01")
        udf_layout.addWidget(self.UDFVersion)
        udf_layout.addStretch()
        layout.addLayout(udf_layout)
        
        # 复制 UDF 2.50 元数据
        self.Copy_UDF_2dot50_metadata = QCheckBox("复制 UDF 2.50 元数据")
        layout.addWidget(self.Copy_UDF_2dot50_metadata)
        
        # 文件记录大小 (仅NTFS)
        self.file_record_size = QCheckBox("文件记录大小 (仅NTFS)")
        layout.addWidget(self.file_record_size)
        
        # 卷大小
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("卷大小（0为不指定）:"))
        self.size = QSpinBox()
        size_layout.addWidget(self.size)
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # 每面磁道数
        tracks_layout = QHBoxLayout()
        tracks_layout.addWidget(QLabel("每面磁道数（0为不指定）:"))
        self.tracks = QSpinBox()
        tracks_layout.addWidget(self.tracks)
        tracks_layout.addStretch()
        layout.addLayout(tracks_layout)
        
        # 每道扇区数
        sectors_layout = QHBoxLayout()
        sectors_layout.addWidget(QLabel("每道扇区数（0为不指定）:"))
        self.sectors = QSpinBox()
        sectors_layout.addWidget(self.sectors)
        sectors_layout.addStretch()
        layout.addLayout(sectors_layout)
        
        # 低级格式化
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("低级格式化次数（0为不指定）:"))
        self.count = QSpinBox()
        count_layout.addWidget(self.count)
        count_layout.addStretch()
        layout.addLayout(count_layout)
        
        # 短文件名支持
        self.short_name_support = QCheckBox("短文件名支持")
        layout.addWidget(self.short_name_support)
        
        # TXF (仅NTFS)
        self.TXF = QCheckBox("TXF (仅NTFS)")
        layout.addWidget(self.TXF)
        
        # ReFS完整性
        self.ReFS_integrity = QCheckBox("ReFS完整性")
        layout.addWidget(self.ReFS_integrity)
        
        # NTFS直接访问存储
        self.DAX = QCheckBox("NTFS直接访问存储")
        layout.addWidget(self.DAX)
        
        # NTFS日志文件大小
        logsize_layout = QHBoxLayout()
        logsize_layout.addWidget(QLabel("日志文件大小（MB，最小为2）:"))
        self.LogSize = QSpinBox()
        logsize_layout.addWidget(self.LogSize)
        logsize_layout.addStretch()
        layout.addLayout(logsize_layout)
        
        # 禁用NTFS修复日志
        self.NoRepairLogs = QCheckBox("禁用NTFS修复日志")
        layout.addWidget(self.NoRepairLogs)
        
        # 开发人员驱动器
        self.DevDrv = QCheckBox("开发人员驱动器")
        layout.addWidget(self.DevDrv)
        
        # 使用SHA-256校验 (仅ReFS)
        self.SHA256Checksums = QCheckBox("使用SHA-256校验 (仅ReFS)")
        layout.addWidget(self.SHA256Checksums)
    
    def load_presets(self):
        """加载预设文件"""
        presets_path = os.path.join(os.path.dirname(__file__), 'presets.json')
        try:
            with open(presets_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            QMessageBox.warning(self, "警告", f"预设文件 'presets.json' 未找到。")
            return {}
        except json.JSONDecodeError:
            QMessageBox.warning(self, "警告", f"预设文件 'presets.json' 格式错误。")
            return {}
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载预设文件时出错: {str(e)}")
            return {}

    def create_presets(self):
        """创建预设场景部分"""
        group = QGroupBox("预设场景")
        layout = QHBoxLayout()
        
        self.preset_combo = QComboBox()
        preset_names = ["自定义"] + list(self.presets_data.keys())
        self.preset_combo.addItems(preset_names)
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)
        
        layout.addWidget(QLabel("预设:"))
        layout.addWidget(self.preset_combo)
        layout.addStretch()
        
        group.setLayout(layout)
        self.main_layout.addWidget(group)
    
    def apply_preset(self, index):
        """应用预设"""
        preset_name = self.preset_combo.itemText(index)
        
        if preset_name == "自定义":
            # 用户选择自定义时，可以选择保留当前设置或重置为默认值
            # 这里我们选择保留当前设置，所以不做任何操作
            return
            
        if preset_name in self.presets_data:
            preset_config = self.presets_data[preset_name]
            
            # 应用所有控件配置
            self.fs_combo.setCurrentText(preset_config.get("fs", "NTFS"))
            self.cluster_combo.setCurrentText(preset_config.get("cluster", "默认"))
            self.quick_format.setChecked(preset_config.get("quick_format", True))
            self.enable_compression.setChecked(preset_config.get("enable_compression", False))
            self.volume_label.setText(preset_config.get("volume_label", ""))
            self.Force_volume_disassembly.setChecked(preset_config.get("Force_volume_disassembly", False))
            self.UDFVersion.setCurrentText(preset_config.get("UDFVersion", "2.01"))
            self.Copy_UDF_2dot50_metadata.setChecked(preset_config.get("Copy_UDF_2dot50_metadata", False))
            self.file_record_size.setChecked(preset_config.get("file_record_size", False))
            self.size.setValue(preset_config.get("size", 0))
            self.tracks.setValue(preset_config.get("tracks", 0))
            self.sectors.setValue(preset_config.get("sectors", 0))
            self.count.setValue(preset_config.get("count", 0))
            self.short_name_support.setChecked(preset_config.get("short_name_support", False))
            self.TXF.setChecked(preset_config.get("TXF", False))
            self.ReFS_integrity.setChecked(preset_config.get("ReFS_integrity", False))
            self.DAX.setChecked(preset_config.get("DAX", False))
            self.LogSize.setValue(preset_config.get("LogSize", 0))
            self.NoRepairLogs.setChecked(preset_config.get("NoRepairLogs", False))
            self.DevDrv.setChecked(preset_config.get("DevDrv", False))
            self.SHA256Checksums.setChecked(preset_config.get("SHA256Checksums", False))
        else:
            QMessageBox.warning(self, "警告", f"未找到名为 '{preset_name}' 的预设配置。")
    
    def create_action_buttons(self):
        """创建操作按钮"""
        layout = QHBoxLayout()
        
        format_btn = QPushButton("格式化")
        format_btn.clicked.connect(self.execute_format)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.close)
        
        layout.addStretch()
        layout.addWidget(format_btn)
        layout.addWidget(cancel_btn)
        
        self.main_layout.addLayout(layout)
        
        # 设置最小尺寸确保滚动条正确显示
        self.main_widget.setMinimumSize(380, 800)
    
    def execute_format(self):
        """执行格式化命令"""
        drive = self.drive_combo.currentText()
        if not drive:
            QMessageBox.warning(self, "错误", "请选择要格式化的驱动器")
            return
        
        # 构建format命令
        cmd = f"format {drive}"
        
        # 文件系统
        fs = self.fs_combo.currentText()
        cmd += f" /FS:{fs}"
        
        # 卷标
        label = self.volume_label.text().strip()
        if label:
            cmd += f" /V:{label}"
        
        # 快速格式化
        if self.quick_format.isChecked():
            cmd += " /Q"
        
        # 压缩
        if self.enable_compression.isChecked() and fs == "NTFS":
            cmd += " /C"
        
        # 强制卸除卷
        if self.Force_volume_disassembly.isChecked():
            cmd += " /X"

        # UDF 版本
        if self.fs_combo.currentText() == "UDF":
            cmd += f" /R:{self.UDFVersion.currentText()}"

        # 复制 UDF 2.50 元数据
        if self.Copy_UDF_2dot50_metadata.isChecked() and fs == "UDF" and self.UDFVersion.currentText() == "2.50":
            cmd += " /D"

        # 文件记录大小 (仅NTFS)
        if self.file_record_size.isChecked() and fs == "NTFS":
            cmd += " /L:{file_record_size}"

        # 分配单元大小
        cluster = self.cluster_combo.currentText()
        if cluster != "默认":
            cmd += f" /A:{cluster}"

        # 卷大小
        if self.size.value() != 0:
            cmd += " /F:{size}"

        # 每面磁道数
        if self.tracks.value() != 0:
            cmd += " /T:{tracks}"

        # 每道扇区数
        if self.sectors.value() != 0:
            cmd += " /N:{sectors}"

        # 低级格式化和写零次数
        if not self.quick_format.isChecked() and self.count.value() != 0:
            cmd += " /P:{count}"

        # 短文件名支持
        if self.short_name_support.isChecked():
            cmd += " /S:{short_name_state}"

        # TXF (仅NTFS)
        if self.TXF.isChecked() and fs == "NTFS":
            cmd += " /TXF:{TXF_state}"

        # ReFS完整性
        if self.ReFS_integrity.isChecked() and fs == "ReFS":
            cmd += " /I:{integrity_state}"

        # NTFS直接访问存储 (仅NTFS)
        if self.DAX.isChecked() and fs == "NTFS":
            cmd += " /DAX:{DAX_state}"

        # NTFS日志文件大小 (仅NTFS)
        if self.LogSize.value() != 0 and fs == "NTFS":
            cmd += f" /LogSize:{self.LogSize.value()}"

        # 禁用NTFS修复日志 (仅NTFS)
        if self.NoRepairLogs.isChecked() and fs == "NTFS":
            cmd += " /NoRepairLogs"

        # 开发人员驱动器
        if self.DevDrv.isChecked():
            cmd += " /DevDrv"

        # 使用SHA-256校验 (仅ReFS)
        if self.SHA256Checksums.isChecked() and fs == "ReFS":
            cmd += " /SHA256Checksums"

        # 确认提示
        reply = QMessageBox.question(self, "确认", 
                                   f"确定要格式化 {drive} 吗？\n命令: {cmd}",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # 执行命令
                process = subprocess.Popen(cmd, shell=True, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         stdin=subprocess.PIPE)
                
                # 处理输出
                while True:
                    output = process.stdout.readline()
                    if output == b'' and process.poll() is not None:
                        break
                    if output:
                        self.handle_output(output.decode())
                
                QMessageBox.information(self, "完成", "格式化操作已完成")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"格式化失败: {str(e)}")
    
    def handle_output(self, output):
        """处理命令输出"""
        try:
            # 尝试解码输出，使用更健壮的解码方式
            if isinstance(output, bytes):
                # 优先尝试GBK编码，再尝试ANSI编码
                try:
                    output = output.decode('gbk', errors='replace')
                except UnicodeDecodeError:
                    try:
                        output = output.decode('ansi', errors='replace')
                    except UnicodeDecodeError:
                        output = output.decode('utf-8', errors='replace')
            
            # 处理特定输出
            if "输入卷标" in output or "Enter current volume label" in output:
                reply = QMessageBox.question(self, "卷标确认", 
                                           "检测到需要输入当前卷标，是否继续？",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # 发送回车继续
                    self.process.stdin.write(b"\n")
                    self.process.stdin.flush()
            
            # 记录输出到控制台
            print(output.strip())
            
        except Exception as e:
            print(f"处理输出时出错: {str(e)}")
            QMessageBox.warning(self, "错误", f"处理输出时出错: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BetterFormatGUI()
    window.show()
    sys.exit(app.exec_())