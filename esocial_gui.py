#!/usr/bin/env python3
"""
Interface gráfica para o projeto de migração do eSocial
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
import os
import sys
from pathlib import Path

# Configuração mínima inicial - apenas src
pasta_raiz = Path(__file__).parent
sys.path.insert(0, str(pasta_raiz / "src"))

# Importar módulos
from src.configuracao.configuracoes import Configuracoes
from src.banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from src.processadores.processador_xml import ProcessadorXML
from src.exportadores.exportador_templates_empresa import ExportadorTemplatesEmpresa

# Proteger sys.stdout e sys.stderr
if sys.stdout is None:
    import os
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    import os
    sys.stderr = open(os.devnull, 'w')


class EsocialMigrationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("eSocial Migration Tool")
        self.root.geometry("800x600")
        
        # Variáveis de controle
        self.processing = False
        self.arquivo_var = tk.StringVar()
        self.pasta_var = tk.StringVar(value="data/output")
        self.db_path_var = tk.StringVar(value="data/db/esocial.db")
        
        # Configurar logging
        self.logger = self._configurar_logging()
        
        # Configurar interface
        self._configurar_tamanho_tela()
        self.create_widgets()
        
        # Configurar evento de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _configurar_logging(self):
        """Configura o sistema de logging"""
        diretorio_logs = Path("logs")
        diretorio_logs.mkdir(exist_ok=True)
        handlers = [logging.FileHandler(diretorio_logs / 'application.log')]
        if sys.stdout:
            handlers.append(logging.StreamHandler(sys.stdout))
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        return logging.getLogger("esocial_gui")

    def _configurar_tamanho_tela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="eSocial Migration Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Seleção de diretório de entrada
        ttk.Label(main_frame, text="Diretório XML:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.arquivo_var, width=50).grid(row=1, column=1, sticky='we', pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Procurar", command=self.selecionar_diretorio_xml).grid(row=1, column=2, pady=5)
        
        # Seleção de diretório de saída
        ttk.Label(main_frame, text="Diretório Saída:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.pasta_var, width=50).grid(row=2, column=1, sticky='we', pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Procurar", command=self.selecionar_diretorio_saida).grid(row=2, column=2, pady=5)
        
        # Caminho do banco de dados
        ttk.Label(main_frame, text="Banco de Dados:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.db_path_var, width=50).grid(row=3, column=1, sticky='we', pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Procurar", command=self.selecionar_banco_dados).grid(row=3, column=2, pady=5)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=4, column=0, columnspan=3, sticky='nsew', pady=(20, 0))
        main_frame.rowconfigure(4, weight=1)
        
        # Aba de processamento
        self.process_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.process_frame, text="Processar")
        
        # Botão de processamento
        self.process_button = ttk.Button(self.process_frame, text="Processar Arquivos XML", 
                                        command=self.start_processing, state=tk.NORMAL)
        self.process_button.pack(pady=20)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(self.process_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Pronto para processar")
        self.status_label = ttk.Label(self.process_frame, textvariable=self.status_var)
        self.status_label.pack(pady=10)
        
        # Aba de exportação
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="Exportar")
        
        # Botão de exportação
        self.export_button = ttk.Button(self.export_frame, text="Exportar Templates Empresa", 
                                       command=self.start_export, state=tk.DISABLED)
        self.export_button.pack(pady=20)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=5, column=0, columnspan=3, sticky='nsew', pady=(10, 0))
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def selecionar_diretorio_xml(self):
        """Seleciona o diretório com arquivos XML"""
        diretorio = filedialog.askdirectory(title="Selecione o diretório com arquivos XML")
        if diretorio:
            self.arquivo_var.set(diretorio)

    def selecionar_diretorio_saida(self):
        """Seleciona o diretório de saída"""
        diretorio = filedialog.askdirectory(title="Selecione o diretório de saída")
        if diretorio:
            self.pasta_var.set(diretorio)

    def selecionar_banco_dados(self):
        """Seleciona o arquivo de banco de dados"""
        arquivo = filedialog.asksaveasfilename(
            title="Selecione o arquivo de banco de dados",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All files", "*.*")]
        )
        if arquivo:
            self.db_path_var.set(arquivo)

    def log_message(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def start_processing(self):
        """Inicia o processamento em thread separada"""
        if not self.arquivo_var.get():
            messagebox.showerror("Erro", "Selecione o diretório com arquivos XML")
            return
            
        self.processing = True
        self.process_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Processando...")
        
        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=self._processar_arquivos)
        thread.daemon = True
        thread.start()

    def _processar_arquivos(self):
        """Processa os arquivos XML"""
        try:
            # Mensagem amigável ao usuário
            self.log_message("Iniciando processamento dos arquivos XML...")
            
            # Configurações
            configuracoes = Configuracoes()
            configuracoes.CAMINHO_ENTRADA = Path(self.arquivo_var.get())
            configuracoes.CAMINHO_SAIDA = Path(self.pasta_var.get())
            configuracoes.CAMINHO_BANCO_DADOS = Path(self.db_path_var.get())
            
            # Criar diretórios se não existirem
            Path(configuracoes.CAMINHO_SAIDA).mkdir(parents=True, exist_ok=True)
            Path(configuracoes.CAMINHO_BANCO_DADOS).parent.mkdir(parents=True, exist_ok=True)
            
            # Deletar banco de dados existente
            if os.path.exists(configuracoes.CAMINHO_BANCO_DADOS):
                os.remove(configuracoes.CAMINHO_BANCO_DADOS)
                self.log_message("Banco de dados anterior removido")
            
            # Criar gerenciador de banco de dados
            gerenciador_bd = GerenciadorBancoDados(configuracoes.CAMINHO_BANCO_DADOS)
            self.log_message("Banco de dados inicializado")
            
            # Processar arquivos XML
            processador_xml = ProcessadorXML(gerenciador_bd, configuracoes)
            
            # Converter string para Path se necessário
            caminho_entrada = configuracoes.CAMINHO_ENTRADA
            if isinstance(caminho_entrada, str):
                caminho_entrada = Path(caminho_entrada)
            
            total_processado = processador_xml.processar_diretorio(caminho_entrada)
            
            # Mensagem amigável ao usuário
            self.log_message(f"Processamento concluído: {total_processado} arquivos processados")
            
            # Atualizar interface na thread principal
            self.root.after(0, self._processamento_concluido)
        except Exception as e:
            self.logger.error(f"Erro durante processamento: {e}", exc_info=True)
            self.root.after(0, lambda: self._erro_processamento(str(e)))

    def _processamento_concluido(self):
        """Chamado quando o processamento é concluído"""
        self.processing = False
        self.progress.stop()
        self.process_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)
        self.status_var.set("Processamento concluído")
        messagebox.showinfo("Sucesso", "Arquivos XML processados com sucesso!")

    def _erro_processamento(self, erro):
        """Chamado quando há erro no processamento"""
        self.processing = False
        self.progress.stop()
        self.process_button.config(state=tk.NORMAL)
        self.status_var.set("Erro no processamento")
        self.log_message(f"ERRO: {erro}")
        messagebox.showerror("Erro", f"Erro durante processamento:\n{erro}")

    def start_export(self):
        """Inicia a exportação em thread separada"""
        self.export_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Exportando...")
        
        # Executar em thread separada
        thread = threading.Thread(target=self._exportar_templates)
        thread.daemon = True
        thread.start()

    def _exportar_templates(self):
        """Exporta os templates Empresa"""
        try:
            # Mensagem amigável ao usuário
            self.log_message("Iniciando exportação dos templates Empresa...")
            
            # Configurações
            configuracoes = Configuracoes()
            configuracoes.CAMINHO_SAIDA = Path(self.pasta_var.get())
            configuracoes.CAMINHO_BANCO_DADOS = Path(self.db_path_var.get())
            
            # Verificar se banco existe
            if not os.path.exists(configuracoes.CAMINHO_BANCO_DADOS):
                raise Exception("Banco de dados não encontrado. Execute o processamento primeiro.")
            
            # Criar gerenciador de banco de dados
            gerenciador_bd = GerenciadorBancoDados(configuracoes.CAMINHO_BANCO_DADOS)
            
            # Exportar templates
            exportador_templates = ExportadorTemplatesEmpresa(gerenciador_bd, configuracoes)
            templates_processados = exportador_templates.exportar_todos_templates()
            
            # Mensagem amigável ao usuário
            self.log_message(f"Exportação concluída: {templates_processados} templates exportados")
            
            # Atualizar interface na thread principal
            self.root.after(0, self._exportacao_concluida)
        except Exception as e:
            self.logger.error(f"Erro durante exportação: {e}", exc_info=True)
            self.root.after(0, lambda: self._erro_exportacao(str(e)))

    def _exportacao_concluida(self):
        """Chamado quando a exportação é concluída"""
        self.progress.stop()
        self.export_button.config(state=tk.NORMAL)
        self.status_var.set("Exportação concluída")
        messagebox.showinfo("Sucesso", f"Templates exportados para {self.pasta_var.get()}")

    def _erro_exportacao(self, erro):
        """Chamado quando há erro na exportação"""
        self.progress.stop()
        self.export_button.config(state=tk.NORMAL)
        self.status_var.set("Erro na exportação")
        self.log_message(f"ERRO: {erro}")
        messagebox.showerror("Erro", f"Erro durante exportação:\n{erro}")

    def on_closing(self):
        """Tratamento do fechamento da janela"""
        if self.processing:
            if messagebox.askokcancel("Fechar", "Processamento em andamento. Deseja realmente fechar?"):
                self.root.destroy()
                return True
            return False
        else:
            self.root.destroy()
            return True


def main():
    """Função principal da interface gráfica"""
    root = tk.Tk()
    app = EsocialMigrationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
