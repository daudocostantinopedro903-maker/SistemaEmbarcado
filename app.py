#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA EMBARCADO - MONITORAMENTO ELÉTRICO v4.1
Sistema Integrado de Monitoramento de Corrente Elétrica - UniRovuma
Universidade Rovuma - Faculdade de Engenharia
Versão: 4.1.0 (Corrigido - Gestão de Usuários)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import random
import io
import csv
import threading
import time

app = Flask(__name__)
app.secret_key = 'rovuma_engenharia_monitoramento_2026_seguro_v4'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# ============================================================
# CONFIGURAÇÕES
# ============================================================
SISTEMA_NOME = "SISTEMA EMBARCADO"
SISTEMA_SUB = "SISTEMA INTEGRADO DE MONITORAMENTO DE CORRENTE ELÉTRICA_UNIROVUMA"
UNIVERSIDADE = "UNIVERSIDADE ROVUMA"
FACULDADE = "FACULDADE DE ENGENHARIA"
VERSAO = "4.1.0"

# ============================================================
# BANCO DE DADOS
# ============================================================
class Database:
    def __init__(self):
        self.usuarios = {
            "daudo": {
                "id": 1,
                "username": "daudo",
                "password": self._hash_password("daudo"),
                "nome": "Administrador Daudo",
                "email": "daudo@rovuma.ac.mz",
                "tipo": "admin",
                "ativo": True,
                "ultimo_acesso": None,
                "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        }

        # SALAS REDUZIDAS CONFORME SOLICITADO
        self.salas = {
            "sala_informatica": {
                "id": "sala_informatica",
                "nome": "SALA DE INFORMÁTICA",
                "bloco": "Bloco A",
                "localizacao": "Bloco A ",
                "status": "OPERACIONAL",
                "equipamentos": {
                    "infraestrutura_rede": [
                        {
                            "id": "rack_001",
                            "nome": "RACK DE REDE",
                            "tipo": "Rack de Rede",
                            "estado": True,
                            "temperatura": 36.5,
                            "corrente": 4.2,
                            "tensao": 220,
                            "potencia": 924,
                            "fator_potencia": 0.88,
                            "frequencia": 50.0,
                            "ise": 95,
                            "ultima_manutencao": "15/04/2026",
                            "horas_operacao": 8760,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        }
                    ],
                    "climatizacao": [
                        {
                            "id": "ac_001",
                            "nome": "AR CONDICIONADO",
                            "tipo": "Ar Condicionado",
                            "estado": True,
                            "temperatura": 38.7,
                            "corrente": 8.5,
                            "tensao": 220,
                            "potencia": 1870,
                            "fator_potencia": 0.92,
                            "frequencia": 50.0,
                            "ise": 80,
                            "ultima_manutencao": "15/04/2026",
                            "horas_operacao": 2450,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        }
                    ],
                    "cargas_gerais": [
                        {
                            "id": "comp_001",
                            "nome": "COMPUTADOR PRINCIPAL",
                            "tipo": "Computador Principal",
                            "estado": True,
                            "temperatura": 42.5,
                            "corrente": 3.2,
                            "tensao": 220,
                            "potencia": 704,
                            "fator_potencia": 0.85,
                            "frequencia": 50.0,
                            "ise": 88,
                            "ultima_manutencao": "02/05/2026",
                            "horas_operacao": 3600,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        },
                        {
                            "id": "dc_001",
                            "nome": "DATA CENTER",
                            "tipo": "Data Center",
                            "estado": True,
                            "temperatura": 45.2,
                            "corrente": 22.5,
                            "tensao": 220,
                            "potencia": 4950,
                            "fator_potencia": 0.90,
                            "frequencia": 50.0,
                            "ise": 72,
                            "ultima_manutencao": "10/05/2026",
                            "horas_operacao": 8760,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        }
                    ]
                }
            },
            "faculdade_engenharia": {
                "id": "faculdade_engenharia",
                "nome": "FACULDADE DE ENGENHARIA",
                "bloco": "Bloco D",
                "localizacao": "Bloco D ",
                "status": "OPERACIONAL",
                "equipamentos": {
                    "climatizacao": [
                        {
                            "id": "ac_004",
                            "nome": "AR CONDICIONADO",
                            "tipo": "Ar Condicionado",
                            "estado": True,
                            "temperatura": 34.5,
                            "corrente": 6.2,
                            "tensao": 220,
                            "potencia": 1364,
                            "fator_potencia": 0.89,
                            "frequencia": 50.0,
                            "ise": 92,
                            "ultima_manutencao": "22/04/2026",
                            "horas_operacao": 2800,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        }
                    ],
                    "cargas_gerais": [
                        {
                            "id": "ilum_003",
                            "nome": "SISTEMA DE ILUMINAÇÃO",
                            "tipo": "Iluminação",
                            "estado": True,
                            "temperatura": 31.2,
                            "corrente": 3.8,
                            "tensao": 220,
                            "potencia": 836,
                            "fator_potencia": 0.88,
                            "frequencia": 50.0,
                            "ise": 98,
                            "ultima_manutencao": "10/05/2026",
                            "horas_operacao": 4500,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        },
                        {
                            "id": "imp_002",
                            "nome": "IMPRESSORA",
                            "tipo": "Impressora",
                            "estado": True,
                            "temperatura": 32.5,
                            "corrente": 1.5,
                            "tensao": 220,
                            "potencia": 330,
                            "fator_potencia": 0.82,
                            "frequencia": 50.0,
                            "ise": 96,
                            "ultima_manutencao": "01/05/2026",
                            "horas_operacao": 800,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        }
                    ]
                }
            },
            "salas_aulas": {
                "id": "salas_aulas",
                "nome": "SALAS DE AULA",
                "bloco": "Bloco C",
                "localizacao": "Bloco C ",
                "status": "OPERACIONAL",
                "equipamentos": {
                    "cargas_gerais": [
                        {
                            "id": "ilum_aula_001",
                            "nome": "SISTEMA DE ILUMINAÇÃO",
                            "tipo": "Iluminação",
                            "estado": True,
                            "temperatura": 30.5,
                            "corrente": 5.2,
                            "tensao": 220,
                            "potencia": 1144,
                            "fator_potencia": 0.90,
                            "frequencia": 50.0,
                            "ise": 97,
                            "ultima_manutencao": "05/05/2026",
                            "horas_operacao": 3200,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        },
                        {
                            "id": "vent_001",
                            "nome": "SISTEMA DE VENTILAÇÃO",
                            "tipo": "Ventilação",
                            "estado": True,
                            "temperatura": 35.8,
                            "corrente": 4.5,
                            "tensao": 220,
                            "potencia": 990,
                            "fator_potencia": 0.87,
                            "frequencia": 50.0,
                            "ise": 91,
                            "ultima_manutencao": "20/04/2026",
                            "horas_operacao": 5600,
                            "tempo_desligamento_auto": None,
                            "alerta_ativo": False
                        }
                    ]
                }
            }
        }

        self.sala_atual = "sala_informatica"
        self.alarmes_ativos = []
        self.alarmes_historico = []
        self.configuracoes = {
            "temp_max": 45,
            "corrente_max": 20,
            "tensao_min": 210,
            "tensao_max": 240,
            "intervalo_atualizacao": 5,
            "notificacoes_email": True,
            "tempo_desligamento_auto": 300,
            "limite_desvio_corrente": 15,
        }
        self.logs_sistema = []
        self.historico_dados = {}
        self.historico_equipamentos = {}
        self._adicionar_log("Sistema iniciado", "sistema")
        self._inicializar_historico()
        self._inicializar_historico_equipamentos()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _inicializar_historico(self):
        agora = datetime.now()
        for sala_id, sala in self.salas.items():
            self.historico_dados[sala_id] = []
            for i in range(24):
                hora = agora - timedelta(hours=i)
                self.historico_dados[sala_id].append({
                    "hora": hora.strftime("%H:%M"),
                    "corrente_total": round(random.uniform(10, 60), 1),
                    "potencia_total": round(random.uniform(2000, 15000), 0),
                    "temperatura_media": round(random.uniform(28, 48), 1),
                    "frequencia": round(50.0 + random.uniform(-0.5, 0.5), 1)
                })

    def _inicializar_historico_equipamentos(self):
        for sala_id, sala in self.salas.items():
            for categoria, equipamentos in sala["equipamentos"].items():
                for equip in equipamentos:
                    equip_id = equip["id"]
                    self.historico_equipamentos[equip_id] = []
                    for i in range(30):
                        dia = datetime.now() - timedelta(days=i)
                        self.historico_equipamentos[equip_id].append({
                            "data": dia.strftime("%d/%m/%Y"),
                            "corrente_media": round(equip["corrente"] * random.uniform(0.85, 1.15), 2),
                            "potencia_media": round(equip["potencia"] * random.uniform(0.85, 1.15), 0),
                            "temperatura_max": round(equip.get("temperatura", 35) * random.uniform(0.9, 1.2), 1),
                            "horas_operacao": equip["horas_operacao"] - (i * 8),
                            "anomalia": random.random() < 0.05
                        })

    def _adicionar_log(self, mensagem, tipo="info"):
        self.logs_sistema.append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "mensagem": mensagem,
            "tipo": tipo
        })

    def verificar_credenciais(self, username, password):
        if username in self.usuarios:
            hashed = self._hash_password(password)
            if self.usuarios[username]["password"] == hashed:
                if self.usuarios[username]["ativo"]:
                    self.usuarios[username]["ultimo_acesso"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    self._adicionar_log(f"Login: {username}", "login")
                    return True
        return False

    def adicionar_usuario(self, dados):
        if dados["username"] in self.usuarios:
            return False, "Usuário já existe!"
        dados["password"] = self._hash_password(dados["password"])
        dados["id"] = len(self.usuarios) + 1
        dados["data_criacao"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        dados["ultimo_acesso"] = None
        dados["ativo"] = True
        self.usuarios[dados["username"]] = dados
        self._adicionar_log(f"Novo usuário: {dados['username']}", "usuario")
        return True, "Usuário cadastrado com sucesso!"

    def editar_usuario(self, username, dados):
        if username not in self.usuarios:
            return False, "Usuário não encontrado!"
        user = self.usuarios[username]
        if "nome" in dados:
            user["nome"] = dados["nome"]
        if "email" in dados:
            user["email"] = dados["email"]
        if "tipo" in dados:
            user["tipo"] = dados["tipo"]
        if "ativo" in dados:
            user["ativo"] = dados["ativo"]
        if "password" in dados and dados["password"]:
            user["password"] = self._hash_password(dados["password"])
        self._adicionar_log(f"Usuário {username} atualizado", "usuario")
        return True, "Usuário atualizado com sucesso!"

    def excluir_usuario(self, username):
        if username not in self.usuarios:
            return False, "Usuário não encontrado!"
        if username == "daudo":
            return False, "Não é possível excluir o administrador principal!"
        del self.usuarios[username]
        self._adicionar_log(f"Usuário {username} excluído", "usuario")
        return True, "Usuário excluído com sucesso!"

    def promover_usuario(self, username, novo_tipo):
        if username not in self.usuarios:
            return False, "Usuário não encontrado!"
        if novo_tipo not in ["admin", "operador"]:
            return False, "Tipo de usuário inválido!"
        self.usuarios[username]["tipo"] = novo_tipo
        self._adicionar_log(f"Usuário {username} promovido para {novo_tipo}", "usuario")
        return True, f"Usuário {username} atualizado para {novo_tipo}!"

    def alternar_estado(self, equip_id, sala_id=None):
        if not sala_id:
            sala_id = self.sala_atual
        sala = self.salas.get(sala_id)
        if not sala:
            return None
        for categoria, equipamentos in sala["equipamentos"].items():
            for equip in equipamentos:
                if equip["id"] == equip_id:
                    equip["estado"] = not equip["estado"]
                    equip["alerta_ativo"] = False
                    equip["tempo_desligamento_auto"] = None
                    if not equip["estado"]:
                        equip["corrente"] = 0
                        equip["potencia"] = 0
                        equip["frequencia"] = 0.0
                    else:
                        equip["corrente"] = round(random.uniform(0.5, 15.0), 1)
                        equip["potencia"] = round(equip["corrente"] * equip["tensao"] * equip["fator_potencia"], 0)
                        equip["frequencia"] = round(50.0 + random.uniform(-0.5, 0.5), 1)
                    acao = "LIGADO" if equip["estado"] else "DESLIGADO"
                    self._adicionar_log(f"{equip['nome']} {acao} ({sala['nome']})", "acao")
                    self._verificar_alarmes()
                    return equip["estado"]
        return None

    def _verificar_alarmes(self):
        self.alarmes_ativos = []
        agora = datetime.now()

        for sala_id, sala in self.salas.items():
            for categoria, equipamentos in sala["equipamentos"].items():
                for equip in equipamentos:
                    if equip.get("temperatura") and equip["temperatura"] > self.configuracoes["temp_max"]:
                        alarme_id = f"alarm_temp_{equip['id']}"
                        if not equip.get("alerta_ativo"):
                            equip["alerta_ativo"] = True
                            equip["tempo_desligamento_auto"] = agora + timedelta(seconds=self.configuracoes["tempo_desligamento_auto"])

                        tempo_restante = ""
                        if equip.get("tempo_desligamento_auto"):
                            restante = (equip["tempo_desligamento_auto"] - agora).total_seconds()
                            if restante > 0:
                                tempo_restante = f"Desligamento automático em {int(restante/60)}min {int(restante%60)}s"
                            else:
                                equip["estado"] = False
                                equip["corrente"] = 0
                                equip["potencia"] = 0
                                equip["frequencia"] = 0.0
                                equip["alerta_ativo"] = False
                                equip["tempo_desligamento_auto"] = None
                                self._adicionar_log(f"DESLIGAMENTO AUTOMÁTICO: {equip['nome']} por temperatura crítica", "critico")
                                tempo_restante = "DESLIGADO AUTOMATICAMENTE"

                        self.alarmes_ativos.append({
                            "id": alarme_id,
                            "equipamento": equip["nome"],
                            "sala": sala["nome"],
                            "sala_id": sala_id,
                            "tipo": "critico",
                            "mensagem": f"Temperatura alta: {equip['temperatura']}°C (limite: {self.configuracoes['temp_max']}°C)",
                            "acao_requerida": tempo_restante,
                            "valor": equip["temperatura"],
                            "limite": self.configuracoes["temp_max"],
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "status": "NÃO RESOLVIDO",
                            "auto_shutdown": True
                        })

                    if equip.get("corrente") and equip["corrente"] > self.configuracoes["corrente_max"]:
                        alarme_id = f"alarm_corr_{equip['id']}"
                        if not equip.get("alerta_ativo"):
                            equip["alerta_ativo"] = True
                            equip["tempo_desligamento_auto"] = agora + timedelta(seconds=self.configuracoes["tempo_desligamento_auto"])

                        tempo_restante = ""
                        if equip.get("tempo_desligamento_auto"):
                            restante = (equip["tempo_desligamento_auto"] - agora).total_seconds()
                            if restante > 0:
                                tempo_restante = f"Desligamento automático em {int(restante/60)}min {int(restante%60)}s"
                            else:
                                equip["estado"] = False
                                equip["corrente"] = 0
                                equip["potencia"] = 0
                                equip["frequencia"] = 0.0
                                equip["alerta_ativo"] = False
                                equip["tempo_desligamento_auto"] = None
                                self._adicionar_log(f"DESLIGAMENTO AUTOMÁTICO: {equip['nome']} por sobrecorrente", "critico")
                                tempo_restante = "DESLIGADO AUTOMATICAMENTE"

                        self.alarmes_ativos.append({
                            "id": alarme_id,
                            "equipamento": equip["nome"],
                            "sala": sala["nome"],
                            "sala_id": sala_id,
                            "tipo": "atencao",
                            "mensagem": f"Sobrecorrente: {equip['corrente']}A (limite: {self.configuracoes['corrente_max']}A)",
                            "acao_requerida": tempo_restante,
                            "valor": equip["corrente"],
                            "limite": self.configuracoes["corrente_max"],
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            "status": "NÃO RESOLVIDO",
                            "auto_shutdown": True
                        })

                    if equip.get("tensao"):
                        if equip["tensao"] < self.configuracoes["tensao_min"] or equip["tensao"] > self.configuracoes["tensao_max"]:
                            self.alarmes_ativos.append({
                                "id": f"alarm_tens_{equip['id']}",
                                "equipamento": equip["nome"],
                                "sala": sala["nome"],
                                "sala_id": sala_id,
                                "tipo": "atencao",
                                "mensagem": f"Tensão fora da faixa: {equip['tensao']}V (faixa: {self.configuracoes['tensao_min']}-{self.configuracoes['tensao_max']}V)",
                                "acao_requerida": "Verificar fonte de alimentação",
                                "valor": equip["tensao"],
                                "limite": f"{self.configuracoes['tensao_min']}-{self.configuracoes['tensao_max']}",
                                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                "status": "NÃO RESOLVIDO",
                                "auto_shutdown": False
                            })

                    if equip.get("alerta_ativo") and not any(a["id"].endswith(equip["id"]) for a in self.alarmes_ativos):
                        equip["alerta_ativo"] = False
                        equip["tempo_desligamento_auto"] = None

    def prever_falhas(self, equip_id=None):
        previsoes = []
        equipamentos_analisar = []
        if equip_id:
            equipamentos_analisar = [equip_id]
        else:
            for sala in self.salas.values():
                for categoria in sala["equipamentos"].values():
                    for equip in categoria:
                        equipamentos_analisar.append(equip["id"])

        for eid in equipamentos_analisar:
            historico = self.historico_equipamentos.get(eid, [])
            if len(historico) < 7:
                continue

            correntes = [h["corrente_media"] for h in historico[:14]]
            if len(correntes) < 7:
                continue

            media = sum(correntes) / len(correntes)
            tendencia = correntes[0] - correntes[-1]
            desvio_padrao = (sum((x - media) ** 2 for x in correntes) / len(correntes)) ** 0.5

            temps = [h["temperatura_max"] for h in historico[:14] if h.get("temperatura_max")]
            temp_media = sum(temps) / len(temps) if temps else 0
            temp_max = max(temps) if temps else 0

            anomalias = sum(1 for h in historico[:7] if h.get("anomalia", False))

            probabilidade = 0
            motivos = []

            if abs(tendencia) > media * 0.15:
                probabilidade += 25
                if tendencia > 0:
                    motivos.append("Aumento progressivo do consumo de corrente")
                else:
                    motivos.append("Queda abrupta no consumo de corrente")

            if desvio_padrao > media * 0.1:
                probabilidade += 20
                motivos.append("Alta variabilidade no consumo")

            if temp_max > self.configuracoes["temp_max"]:
                probabilidade += 30
                motivos.append("Temperaturas críticas registradas")
            elif temp_media > self.configuracoes["temp_max"] * 0.85:
                probabilidade += 15
                motivos.append("Temperatura média elevada")

            if anomalias >= 2:
                probabilidade += 20
                motivos.append(f"{anomalias} anomalias detectadas na última semana")

            if probabilidade > 0:
                nome_equip = eid
                sala_nome = ""
                for sala in self.salas.values():
                    for categoria in sala["equipamentos"].values():
                        for equip in categoria:
                            if equip["id"] == eid:
                                nome_equip = equip["nome"]
                                sala_nome = sala["nome"]
                                break

                nivel = "BAIXO"
                if probabilidade >= 70:
                    nivel = "CRÍTICO"
                elif probabilidade >= 40:
                    nivel = "MÉDIO"
                elif probabilidade >= 20:
                    nivel = "BAIXO"

                previsoes.append({
                    "equipamento_id": eid,
                    "equipamento_nome": nome_equip,
                    "sala": sala_nome,
                    "probabilidade": min(100, probabilidade),
                    "nivel": nivel,
                    "motivos": motivos,
                    "recomendacao": "Agendar manutenção preventiva" if probabilidade >= 40 else "Monitorar de perto"
                })

        return sorted(previsoes, key=lambda x: x["probabilidade"], reverse=True)

    def get_resumo_sala(self, sala_id=None):
        if not sala_id:
            sala_id = self.sala_atual
        sala = self.salas.get(sala_id)
        if not sala:
            return {}
        total = 0
        online = 0
        offline = 0
        alertas = 0
        corrente_total = 0
        potencia_total = 0
        temperaturas = []
        for categoria, equipamentos in sala["equipamentos"].items():
            for equip in equipamentos:
                total += 1
                if equip["estado"]:
                    online += 1
                    corrente_total += equip["corrente"]
                    potencia_total += equip["potencia"]
                else:
                    offline += 1
                if equip.get("temperatura") and equip["temperatura"] > self.configuracoes["temp_max"]:
                    alertas += 1
                if equip.get("corrente") and equip["corrente"] > self.configuracoes["corrente_max"]:
                    alertas += 1
                if equip.get("temperatura"):
                    temperaturas.append(equip["temperatura"])
        temp_media = sum(temperaturas) / len(temperaturas) if temperaturas else 0
        status = "OPERACIONAL"
        if offline > 0:
            status = "PARCIAL"
        if alertas > 0:
            status = "ATENÇÃO"
        if offline > 2:
            status = "CRÍTICO"
        sala["status"] = status
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "alertas": alertas,
            "status_geral": status,
            "corrente_total": round(corrente_total, 1),
            "potencia_total": round(potencia_total, 0),
            "temperatura_media": round(temp_media, 1),
            "sala_nome": sala["nome"],
            "sala_bloco": sala["bloco"],
            "sala_localizacao": sala["localizacao"]
        }

    def get_dados_grafico(self, sala_id=None):
        if not sala_id:
            sala_id = self.sala_atual
        return self.historico_dados.get(sala_id, [])

    def get_todos_alarmes(self):
        self._verificar_alarmes()
        return self.alarmes_ativos

    def resolver_alarme(self, alarme_id):
        for alarme in self.alarmes_ativos:
            if alarme["id"] == alarme_id:
                alarme["status"] = "RESOLVIDO"
                alarme["data_resolucao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                self.alarmes_historico.append(alarme)
                for sala in self.salas.values():
                    for categoria in sala["equipamentos"].values():
                        for equip in categoria:
                            if alarme["id"].endswith(equip["id"]):
                                equip["alerta_ativo"] = False
                                equip["tempo_desligamento_auto"] = None
                self._adicionar_log(f"Alarme resolvido: {alarme['equipamento']}", "info")
                return True
        return False

db = Database()

# ============================================================
# DECORADORES
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Faça login para acessar o sistema.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Faça login.', 'warning')
            return redirect(url_for('login'))
        if session.get('user_tipo') != 'admin':
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# ROTAS - AUTENTICAÇÃO (SEM PROTEÇÃO)
# ============================================================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()

        if db.verificar_credenciais(username, password):
            session['user_id'] = db.usuarios[username]["id"]
            session['user_name'] = db.usuarios[username]["nome"]
            session['user_username'] = username
            session['user_tipo'] = db.usuarios[username]["tipo"]
            session.permanent = True
            flash(f'Bem-vindo, {db.usuarios[username]["nome"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'danger')

    return render_template('login.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO)

# ============================================================
# ROTA DE CADASTRO PÚBLICO (mantida para registro externo)
# ============================================================
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        tipo = request.form.get('tipo', 'operador')

        if not all([nome, username, email, password]):
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('cadastro'))

        if password != confirm_password:
            flash('As senhas não coincidem!', 'danger')
            return redirect(url_for('cadastro'))

        if len(password) < 4:
            flash('A senha deve ter pelo menos 4 caracteres!', 'danger')
            return redirect(url_for('cadastro'))

        dados = {
            "nome": nome,
            "username": username,
            "email": email,
            "password": password,
            "tipo": tipo,
            "ativo": True
        }

        sucesso, mensagem = db.adicionar_usuario(dados)
        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('login'))
        else:
            flash(mensagem, 'danger')

    return render_template('cadastro.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO)

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

# ============================================================
# ROTAS PROTEGIDAS - REQUEREM LOGIN
# ============================================================
@app.route('/dashboard')
@login_required
def dashboard():
    sala_id = request.args.get('sala', db.sala_atual)
    if sala_id in db.salas:
        db.sala_atual = sala_id

    resumo = db.get_resumo_sala()
    dados_grafico = db.get_dados_grafico()
    data_atual = datetime.now().strftime("%d/%m/%Y")
    hora_atual = datetime.now().strftime("%H:%M:%S")
    previsoes = db.prever_falhas()

    return render_template('dashboard.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         resumo=resumo,
                         data_atual=data_atual,
                         hora_atual=hora_atual,
                         equipamentos=db.salas[db.sala_atual]["equipamentos"],
                         configuracoes=db.configuracoes,
                         salas=db.salas,
                         sala_atual=db.sala_atual,
                         dados_grafico=dados_grafico,
                         previsoes=previsoes)

@app.route('/monitoramento')
@login_required
def monitoramento():
    sala_id = request.args.get('sala', db.sala_atual)
    if sala_id in db.salas:
        db.sala_atual = sala_id

    return render_template('monitoramento.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         equipamentos=db.salas[db.sala_atual]["equipamentos"],
                         configuracoes=db.configuracoes,
                         salas=db.salas,
                         sala_atual=db.sala_atual,
                         dados_grafico=db.get_dados_grafico())

@app.route('/historico')
@login_required
def historico():
    return render_template('historico.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         logs=db.logs_sistema)

@app.route('/alarmes')
@login_required
def alarmes():
    alarmes_ativos = db.get_todos_alarmes()
    critico = sum(1 for a in alarmes_ativos if a["tipo"] == "critico")
    atencao = sum(1 for a in alarmes_ativos if a["tipo"] == "atencao")

    return render_template('alarmes.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         alarmes=alarmes_ativos,
                         total_critico=critico,
                         total_atencao=atencao,
                         configuracoes=db.configuracoes)

@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        db.configuracoes["temp_max"] = int(request.form.get('temp_max', 45))
        db.configuracoes["corrente_max"] = float(request.form.get('corrente_max', 20))
        db.configuracoes["tensao_min"] = int(request.form.get('tensao_min', 210))
        db.configuracoes["tensao_max"] = int(request.form.get('tensao_max', 240))
        db.configuracoes["intervalo_atualizacao"] = int(request.form.get('intervalo_atualizacao', 5))
        db.configuracoes["notificacoes_email"] = request.form.get('notificacoes_email') == 'on'
        db.configuracoes["tempo_desligamento_auto"] = int(request.form.get('tempo_desligamento_auto', 300))
        db.configuracoes["limite_desvio_corrente"] = int(request.form.get('limite_desvio_corrente', 15))
        db._verificar_alarmes()
        db._adicionar_log("Configurações atualizadas", "config")
        flash('Configurações salvas!', 'success')
        return redirect(url_for('configuracoes'))

    return render_template('configuracoes.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         configuracoes=db.configuracoes)

# ============================================================
# ROTAS DE GESTÃO DE USUÁRIOS (ADMIN)
# ============================================================
@app.route('/usuarios')
@admin_required
def usuarios():
    return render_template('usuarios.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         usuarios=db.usuarios)

@app.route('/usuarios/novo', methods=['GET', 'POST'])
@admin_required
def usuarios_novo():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        tipo = request.form.get('tipo', 'operador')

        if not all([nome, username, email, password]):
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('usuarios_novo'))

        if len(password) < 4:
            flash('A senha deve ter pelo menos 4 caracteres!', 'danger')
            return redirect(url_for('usuarios_novo'))

        dados = {
            "nome": nome,
            "username": username,
            "email": email,
            "password": password,
            "tipo": tipo,
            "ativo": True
        }

        sucesso, mensagem = db.adicionar_usuario(dados)
        flash(mensagem, 'success' if sucesso else 'danger')
        if sucesso:
            return redirect(url_for('usuarios'))
        return redirect(url_for('usuarios_novo'))

    return render_template('usuarios_novo.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'))

@app.route('/usuarios/editar/<username>', methods=['GET', 'POST'])
@admin_required
def usuarios_editar(username):
    if username not in db.usuarios:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('usuarios'))

    user = db.usuarios[username]

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        tipo = request.form.get('tipo', 'operador')
        ativo = request.form.get('ativo') == 'on'
        password = request.form.get('password', '').strip()

        if not nome or not email:
            flash('Nome e email são obrigatórios!', 'danger')
            return redirect(url_for('usuarios_editar', username=username))

        dados = {
            "nome": nome,
            "email": email,
            "tipo": tipo,
            "ativo": ativo
        }
        if password:
            if len(password) < 4:
                flash('A senha deve ter pelo menos 4 caracteres!', 'danger')
                return redirect(url_for('usuarios_editar', username=username))
            dados["password"] = password

        sucesso, mensagem = db.editar_usuario(username, dados)
        flash(mensagem, 'success' if sucesso else 'danger')
        if sucesso:
            return redirect(url_for('usuarios'))

    return render_template('usuarios_editar.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         user=user,
                         username=username)

@app.route('/usuarios/excluir/<username>', methods=['POST'])
@admin_required
def usuarios_excluir(username):
    sucesso, mensagem = db.excluir_usuario(username)
    flash(mensagem, 'success' if sucesso else 'danger')
    return redirect(url_for('usuarios'))

@app.route('/usuarios/promover/<username>', methods=['POST'])
@admin_required
def usuarios_promover(username):
    novo_tipo = request.form.get('tipo', 'operador')
    sucesso, mensagem = db.promover_usuario(username, novo_tipo)
    flash(mensagem, 'success' if sucesso else 'danger')
    return redirect(url_for('usuarios'))

@app.route('/previsoes')
@login_required
def previsoes():
    previsoes_falhas = db.prever_falhas()
    return render_template('previsoes.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         previsoes=previsoes_falhas)

@app.route('/sistema')
@admin_required
def sistema_info():
    return render_template('sistema.html',
                         sistema_nome=SISTEMA_NOME,
                         sistema_sub=SISTEMA_SUB,
                         universidade=UNIVERSIDADE,
                         faculdade=FACULDADE,
                         versao=VERSAO,
                         user_name=session.get('user_name'),
                         user_tipo=session.get('user_tipo'),
                         logs=db.logs_sistema[-50:])

# ============================================================
# EXPORTAR RELATÓRIO
# ============================================================
@app.route('/api/relatorio')
@login_required
def exportar_relatorio():
    sala_id = request.args.get('sala', db.sala_atual)
    sala = db.salas.get(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['RELATORIO DE MONITORAMENTO ELETRICO'])
    writer.writerow([f'Universidade: {UNIVERSIDADE}'])
    writer.writerow([f'Faculdade: {FACULDADE}'])
    writer.writerow([f'Sala: {sala["nome"]}'])
    writer.writerow([f'Bloco: {sala["bloco"]}'])
    writer.writerow([f'Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'])
    writer.writerow([])
    writer.writerow(['ID', 'NOME', 'TIPO', 'ESTADO', 'CORRENTE (A)', 'TENSAO (V)', 
                     'POTENCIA (W)', 'TEMPERATURA (C)', 'FATOR POTENCIA', 'FREQUENCIA (Hz)', 'ISE'])

    for categoria, equipamentos in sala["equipamentos"].items():
        for equip in equipamentos:
            writer.writerow([
                equip['id'], equip['nome'], equip['tipo'],
                'LIGADO' if equip['estado'] else 'DESLIGADO',
                equip['corrente'], equip['tensao'], equip['potencia'],
                equip.get('temperatura', 'N/A'), equip['fator_potencia'],
                equip['frequencia'], equip['ise']
            ])

    resumo = db.get_resumo_sala(sala_id)
    writer.writerow([])
    writer.writerow(['RESUMO'])
    writer.writerow(['Total:', resumo['total']])
    writer.writerow(['Online:', resumo['online']])
    writer.writerow(['Offline:', resumo['offline']])
    writer.writerow(['Alertas:', resumo['alertas']])
    writer.writerow(['Corrente Total:', f"{resumo['corrente_total']} A"])
    writer.writerow(['Potencia Total:', f"{resumo['potencia_total']} W"])
    writer.writerow(['Temperatura Media:', f"{resumo['temperatura_media']} C"])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'relatorio_{sala_id}_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    )

# ============================================================
# API ENDPOINTS
# ============================================================
@app.route('/api/dados')
@login_required
def api_dados():
    sala_id = request.args.get('sala', db.sala_atual)
    if sala_id in db.salas:
        db.sala_atual = sala_id

    sala = db.salas[db.sala_atual]

    for categoria, equipamentos in sala["equipamentos"].items():
        for equip in equipamentos:
            if equip["estado"]:
                if equip.get("temperatura") is not None:
                    variacao = random.uniform(-0.5, 0.5)
                    equip["temperatura"] = round(max(20, min(60, equip["temperatura"] + variacao)), 1)

                variacao_corrente = random.uniform(-0.2, 0.2)
                equip["corrente"] = round(max(0, equip["corrente"] + variacao_corrente), 1)
                equip["potencia"] = round(equip["corrente"] * equip["tensao"] * equip["fator_potencia"], 0)
                equip["frequencia"] = round(50.0 + random.uniform(-0.5, 0.5), 1)

                ise = 100
                if equip.get("temperatura"):
                    if equip["temperatura"] > 40: ise -= 10
                    if equip["temperatura"] > 45: ise -= 20
                if equip["corrente"] > 10: ise -= 5
                equip["ise"] = max(0, min(100, ise))

    db._verificar_alarmes()
    resumo = db.get_resumo_sala()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    return jsonify({
        "equipamentos": sala["equipamentos"],
        "resumo": resumo,
        "data_hora": data_hora,
        "configuracoes": db.configuracoes,
        "sala_atual": db.sala_atual,
        "sala_nome": sala["nome"],
        "alarmes": len(db.alarmes_ativos)
    })

@app.route('/api/alternar/<equip_id>')
@login_required
def api_alternar(equip_id):
    sala_id = request.args.get('sala', db.sala_atual)
    novo_estado = db.alternar_estado(equip_id, sala_id)
    if novo_estado is not None:
        return jsonify({"sucesso": True, "estado": novo_estado})
    return jsonify({"sucesso": False}), 404

@app.route('/api/resumo')
@login_required
def api_resumo():
    sala_id = request.args.get('sala', db.sala_atual)
    return jsonify(db.get_resumo_sala(sala_id))

@app.route('/api/grafico')
@login_required
def api_grafico():
    sala_id = request.args.get('sala', db.sala_atual)
    return jsonify(db.get_dados_grafico(sala_id))

@app.route('/api/alarmes')
@login_required
def api_alarmes():
    return jsonify({
        "alarmes": db.get_todos_alarmes(),
        "total": len(db.alarmes_ativos)
    })

@app.route('/api/alarmes/resolver/<alarme_id>', methods=['POST'])
@login_required
def api_resolver_alarme(alarme_id):
    sucesso = db.resolver_alarme(alarme_id)
    return jsonify({"sucesso": sucesso})

@app.route('/api/previsoes')
@login_required
def api_previsoes():
    return jsonify(db.prever_falhas())

# ============================================================
# ERROS
# ============================================================
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ============================================================
# INICIALIZAÇÃO
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print(f"  {SISTEMA_NOME}")
    print(f"  {SISTEMA_SUB}")
    print(f"  {UNIVERSIDADE} - {FACULDADE}")
    print(f"  Versao: {VERSAO}")
    print("=" * 60)
    print("  Acesse: http://localhost:5000")
    print("  Admin:  daudo / daudo")
    print("  Salas:  sala_informatica (Bloco A)")
    print("          faculdade_engenharia (Bloco D)")
    print("          salas_aulas (Bloco B)")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)