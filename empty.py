    def openFile(self):
        # пользователь выбирает произвольный файл
        name = QFileDialog.getOpenFileName(self, 'Выбрать файл', '',
                                           'Python file (*.py)')[0]
        formats = ['py']
        if name != '' and name.split('.')[-1] in formats:
            f = open(name, 'r', encoding='utf-8').read()
            Page = QSimplePythonEditor()
            Page.setText(f)
            #self.titleBar.setTitle(f'TEXT EDITOR v0.2a - {name}')
            self.tabWidget.addTab(Page, name)
