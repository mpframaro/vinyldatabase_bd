import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db

APP = Flask(__name__)



# Start page
@APP.route('/')
def index():
    stats = {}
    stats = db.execute('''
        SELECT * FROM 
            (SELECT COUNT(*) n_colecionadores FROM COLECIONADORES)
        JOIN
            (SELECT COUNT(*) n_interpretes FROM INTERPRETES)
        JOIN
            (SELECT COUNT(*) n_projetos FROM PROJETOS) 
        JOIN
            (SELECT COUNT(*) n_possui FROM POSSUI)       
        JOIN
            (SELECT COUNT(*) n_musicas FROM MUSICAS)   
        JOIN
            (SELECT COUNT(*) n_fez FROM FEZ) 
        ''').fetchone()
    logging.info(stats)
    return render_template('index.html',stats=stats)





# Projetos
@APP.route('/projetos/')
def list_projetos():
    projetos = db.execute(
      '''
      SELECT p.codigoProjeto as codigoProjetoP, p.nome as nomeP, p.dataLancamento as dataLancamentoP, p.generos as generosP, p.tipo as tipoP, p.formatos as formatosP, p.reviewPitcfork as reviewPitchforkP, i.nome as nomeI, p.codigoInterprete as codigoInterpreteI
      FROM Projetos p JOIN Interpretes i on p.codigoInterprete=i.codigoInterprete
      ORDER BY p.nome
      ''').fetchall()
    return render_template('projeto-list.html', projetos=projetos)



@APP.route('/projetos/<string:codigoP>/')
def get_projeto(codigoP):
  projeto = db.execute(
      '''
      SELECT p.codigoProjeto as codigoProjetoP, p.nome as nomeP, p.dataLancamento as dataLancamentoP, p.generos as generosP, p.tipo as tipoP, p.formatos as formatosP, p.reviewPitcfork as reviewPitchforkP, i.nome as nomeI, p.codigoInterprete as codigoInterpreteI
      FROM Projetos p JOIN Interpretes i on codigoInterpreteI=i.codigoInterprete
      WHERE codigoProjeto = ?
      ''', [codigoP]).fetchone()

  if projeto is None:
        abort(404, 'Código de projeto {} não existe.'.format(codigoP))

  musicas = db.execute(
      '''
      SELECT codigoMusica, m.nome
      FROM Musicas m JOIN Projetos p ON m.codigoProjeto=p.codigoProjeto
      WHERE m.codigoProjeto = ?
      ORDER BY m.nome
      ''', [codigoP]).fetchall()
  return render_template('projeto.html',   
           projeto=projeto, musicas=musicas)



@APP.route('/projetos/search/<expr>/')
def search_projeto(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  projetos = db.execute(
      ''' 
      SELECT p.codigoProjeto as codigoProjetoP, p.nome as nomeProjetoP, p.dataLancamento as dataLancamentoP, p.generos as generosP, p.tipo as tipoP, p.formatos as formatosP, p.reviewPitcfork as reviewPitchforkP, i.nome as nomeI
      FROM Projetos p JOIN Interpretes i on p.codigoInterprete=i.codigoInterprete
      WHERE nomeProjetoP LIKE ?
      ''', [expr]).fetchall()
  return render_template('projeto-search.html',
           search=search,projetos=projetos)





# Músicas
@APP.route('/musicas/')
def list_musicas():
    musicas = db.execute('''
      SELECT m.codigoMusica as codigoMusicaM , m.nome as nomeM, i.codigoInterprete as codigoInterpreteI, i.nome as nomeI
      FROM (Musicas m JOIN Fez f ON m.codigoMusica=f.codigoMusica) JOIN Interpretes i on f.codigoInterprete=i.codigoInterprete
      ORDER BY m.nome
    ''').fetchall()
    return render_template('musica-list.html', musicas=musicas)


@APP.route('/musicas/<string:codigoM>/')
def get_musica(codigoM):
  musica = db.execute(
    '''
    SELECT m.codigoMusica as codigoMusicaM, m.nome as nomeM, m.codigoProjeto as codigoProjetoM, p.codigoProjeto as codigoProjetoP, p.nome as nomeP, p.dataLancamento as dataLancamentoP, p.generos as generosP, p.codigoInterprete as codigoInterpreteP, i.codigoInterprete as codigoInterpreteI, i.nome as nomeI
    FROM (Musicas m JOIN Projetos p ON codigoProjetoM=codigoProjetoP) join Interpretes i on codigoInterpreteP=codigoInterpreteI
    WHERE codigoMusicaM = ?
    ''', [codigoM]).fetchone()

  if musica is None:
     abort(404, 'Música de código {} não existe.'.format(codigoM))

  projetos = db.execute(
    '''
    SELECT m.codigoMusica as codigoMusicaM, m.nome as nomeM, m.codigoProjeto as codigoProjetoM, p.codigoProjeto as codigoProjetoP, p.nome as nomeP, p.dataLancamento as dataLancamentoP, p.codigoInterprete as codigoInterpreteP, i.codigoInterprete as codigoInterpreteI, i.nome as nomeI
    FROM (Musicas m JOIN Projetos p ON codigoProjetoM=codigoProjetoP) join Interpretes i on codigoInterpreteP=codigoInterpreteI
    WHERE codigoMusicaM = ?
    ORDER BY nomeM
    ''', [codigoM]).fetchall()

  return render_template('musica.html', 
           musica=musica, projetos=projetos)


@APP.route('/musicas/search/<expr>/')
def search_musica(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  musicas = db.execute('''
    SELECT m.codigoMusica as codigoMusicaM, m.nome as nomeMusicaM, m.codigoProjeto as codigoProjetoM, p.codigoProjeto as codigoProjetoP, p.nome as nomeP, p.dataLancamento as dataLancamentoP, p.codigoInterprete as codigoInterpreteP, i.codigoInterprete as codigoInterpreteI, i.nome as nomeI
    FROM (Musicas m JOIN Projetos p ON codigoProjetoM=codigoProjetoP) join Interpretes i on codigoInterpreteP=codigoInterpreteI
    WHERE nomeMusicaM LIKE ?
    ''', [expr]).fetchall()

  return render_template('musica-search.html', 
           search=search,musicas=musicas)





# Interpretes
@APP.route('/interpretes/')
def list_interpretes():
    interpretes = db.execute('''
        SELECT i.codigoInterprete as codigoInterpreteI, i.nome as nomeI, i.origem as origemI, i.grammys as grammysI
        FROM Interpretes i
        order by nomeI
    ''').fetchall()
    return render_template('interprete-list.html', interpretes=interpretes)


@APP.route('/interpretes/<string:codigoI>/')
def get_interpretes(codigoI):
  interprete = db.execute(
    '''
    SELECT i.codigoInterprete as codigoInterpreteI, i.nome as nomeI, i.origem as origemI, i.grammys as grammysI, p.codigoProjeto as codigoProjetoP, p.codigoInterprete as codigoInterpreteP, p.nome as nomeP
    FROM Interpretes i join Projetos p on codigoInterpreteI=codigoInterpreteP
    WHERE codigoInterpreteI = ?
    ''', [codigoI]).fetchone()

  if interprete is None:
     abort(404, 'Intérprete de código {} não existe.'.format(codigoI))

  projetos = db.execute(
    '''
    SELECT codigoProjeto, nome, codigoInterprete
    FROM Projetos 
    WHERE codigoInterprete = ?
    ORDER BY nome
    ''', [codigoI]).fetchall()

  return render_template('interprete.html', 
           interprete=interprete, projetos=projetos)


@APP.route('/interpretes/search/<expr>/')
def search_interprete(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  interpretes = db.execute('''
    SELECT codigoInterprete, nome
    FROM Interpretes
    WHERE nome LIKE ?
    ''', [expr]).fetchall()

  return render_template('interprete-search.html', 
           search=search,interpretes=interpretes)





# Colecionadores
@APP.route('/colecionadores/')
def list_colecionadores():
    colecionadores = db.execute('''
        SELECT bi, nome, dataNascimento, dataInicioColecao
        FROM Colecionadores
        ORDER BY nome
    ''').fetchall()
    return render_template('colecionador-list.html', colecionadores=colecionadores)


@APP.route('/colecionadores/<string:codigoC>/')
def get_colecionadores(codigoC):
  colecionador = db.execute(
    '''
    SELECT c.bi as biC, c.nome as nomeC, c.dataNascimento as dataNascimentoC, c.dataInicioColecao as dataInicioColecaoC, po.bi as biPO, po.codigoProjeto as codigoProjetoPO, po.dataCompra as dataCompraPO, pr.codigoProjeto as codigoProjetoPR, pr.nome as nomePR
    FROM (Colecionadores c JOIN Possui po on biC=biPO) join Projetos pr on codigoProjetoPO=codigoProjetoPR
    WHERE biC = ?
    ''', [codigoC]).fetchone()

  if colecionador is None:
     abort(404, 'Colecionador de código {} não existe.'.format(codigoC))

  projetos = db.execute(
    '''
    SELECT c.bi as biC, c.nome as nomeC, c.dataNascimento as dataNascimentoC, c.dataInicioColecao as dataInicioColecaoC, po.bi as biPO, po.codigoProjeto as codigoProjetoPO, po.dataCompra as dataCompraPO, pr.codigoProjeto as codigoProjetoPR, pr.nome as nomePR
    FROM (Colecionadores c JOIN Possui po on biC=biPO) join Projetos pr on codigoProjetoPO=codigoProjetoPR
    WHERE biC = ?
    ''', [codigoC]).fetchall()


  return render_template('colecionador.html', 
           colecionador=colecionador, projetos=projetos)


@APP.route('/colecionadores/search/<expr>/')
def search_colecionadores(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  colecionadores = db.execute('''
    SELECT bi, nome
    FROM Colecionadores
    WHERE nome LIKE ?
    ''', [expr]).fetchall()

  return render_template('colecionador-search.html', 
           search=search,colecionadores=colecionadores)