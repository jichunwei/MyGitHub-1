#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    this->setWindowTitle(QObject::trUtf8("文本编辑器"));

    initMenuBar();
    initToolBar();
    initMainWindow();
    initStatusBar();
    QObject::connect(textEdit,
                     SIGNAL(textChanged()),
                     this,
                     SLOT(dealWithEdit()));


}

void MainWindow::dealWithEdit(){
    statusBar->showMessage(QObject::trUtf8("文本正在编辑...."));
}

void MainWindow::dealWithOpen(){
    dir = QFileDialog::getOpenFileName(this,trUtf8("choose the path"),
                                       QDir::currentPath(),
                                       trUtf8("*.*"));
          //qDebug()<<"Open file Path:"<<dir;

    fileTextEdit(dir);
}

void MainWindow::fileTextEdit(QString){
    openFile = new QFile(dir);
    if(!openFile->open(QFile::ReadOnly|QFile::Text)){
        qDebug()<<"open file failue";
    }
    QString context = openFile->readAll();
    textEdit->clear();
    textEdit->setText(context);

}

MainWindow::~MainWindow()
{
    delete ui;
}


 void MainWindow::initMenuBar(){
    file = new QMenu(this);
    file->setTitle(QObject::trUtf8("文件"));
    editor = new QMenu(this);
    editor->setTitle(QObject::trUtf8("编辑"));
    open = new QAction(this);
    open->setText(QObject::trUtf8("打开"));
    close = new QAction(this);
    close->setText(QObject::trUtf8("关闭"));
    open->setIcon(QIcon(":/icons/open.png"));
    close->setIcon(QIcon(":/icons/close.png"));
    file->addAction(open);
    QObject::connect(open,
                     SIGNAL(triggered()),
                     this,
                     SLOT(dealWithOpen()));
    file->addSeparator();
    file->addAction(close);
    QObject::connect(close,
                     SIGNAL(triggered()),
                     this,
                     SLOT(close()));
    this->menuBar()->addMenu(file);
    this->menuBar()->addSeparator();
    this->menuBar()->addMenu(editor);
}

 void MainWindow::initToolBar(){
        toolBar = new QToolBar();
        toolBar->addAction(open);
        toolBar->addAction(close);

        this->toolBar->addAction(open);
        this->toolBar->addAction(close);
        this->addToolBar(toolBar);
    }

 void MainWindow::initMainWindow(){
    textEdit = new QTextEdit(this);
    this->setCentralWidget(textEdit);
  }

 void MainWindow::initStatusBar(){
    statusBar = new QStatusBar(this);
    this->setStatusBar(statusBar);
 }


