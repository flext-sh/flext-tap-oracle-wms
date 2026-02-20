# FLEXT Tap Oracle WMS

Singer Tap para extracao de dados operacionais de Oracle Warehouse Management System.

Descricao oficial atual: "FLEXT Tap Oracle WMS - Singer Tap for Oracle Warehouse Management System".

## O que este projeto entrega

- Extrai dados logisticos de endpoints WMS.
- Padroniza schema Singer para cadeia de ingestao.
- Apoia atualizacao recorrente de visoes operacionais.

## Contexto operacional

- Entrada: credenciais e escopo Oracle WMS.
- Saida: eventos Singer do dominio logistico.
- Dependencias: flext-oracle-wms e orquestrador de pipeline.

## Estado atual e risco de adocao

- Qualidade: **Alpha**
- Uso recomendado: **Nao produtivo**
- Nivel de estabilidade: em maturacao funcional e tecnica, sujeito a mudancas de contrato sem garantia de retrocompatibilidade.

## Diretriz para uso nesta fase

Aplicar este projeto somente em desenvolvimento, prova de conceito e homologacao controlada, com expectativa de ajustes frequentes ate maturidade de release.
