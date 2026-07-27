const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.static(path.join(__dirname, 'public')));
app.use('/img', express.static(path.join(__dirname, '..', 'img')));

app.get('/', (req, res) => {
  res.render('index', {
    version: '2.0.0',
    appName: 'LIBRYNO',
    developer: 'Wesley Alves',
    library: 'Biblioteca Pública Municipal Maria Margarida Liguori',
    city: 'Nova Friburgo - RJ',
    cnpj: '28606630/0001-23'
  });
});

app.get('/download', (req, res) => {
  res.json({
    status: 'coming_soon',
    message: 'O download estará disponível em breve!',
    platforms: ['Windows', 'Linux', 'Portable']
  });
});

app.listen(PORT, () => {
  console.log(`LIBRYNO Landing Page rodando em http://localhost:${PORT}`);
});
