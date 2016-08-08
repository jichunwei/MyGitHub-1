#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QMenu>
#include <QAction>
#include <QToolBar>
#include <QTextEdit>
#include <QStatusBar>
#include <QFileDialog>
#include <QDebug>

namespace Ui {
    class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();
    void initMenuBar();
    void initToolBar();
    void initMainWindow();
    void initStatusBar();
    void fileTextEdit(QString);


public slots:
    void dealWithEdit();
    void dealWithOpen();

private:
    Ui::MainWindow *ui;
    QMenu *file;
    QMenu *editor;
    QAction *open;
    QAction *close;
    QToolBar *toolBar;
    QTextEdit *textEdit;
    QStatusBar *statusBar;
    QString  dir;
    QFile *openFile;
};

#endif // MAINWINDOW_H
