const { put } = require('@vercel/blob');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const token = process.env.BLOB_READ_WRITE_TOKEN;

if (!token) {
    console.error('ERRO: BLOB_READ_WRITE_TOKEN não encontrado no arquivo .env');
    console.error('Por favor, adicione o token no arquivo .env (você encontra esse token no painel da Vercel, nas configurações do estoque-blob).');
    process.exit(1);
}

const videosDir = path.join(__dirname, 'pagina-vendas', 'videos');

async function uploadVideos() {
    console.log('Iniciando o upload dos vídeos para o Vercel Blob (estoque-blob)...');
    
    try {
        const files = fs.readdirSync(videosDir);
        const videos = files.filter(f => f.endsWith('.mp4') || f.endsWith('.webp') || f.endsWith('.webm'));
        
        if (videos.length === 0) {
            console.log('Nenhum vídeo encontrado no diretório.');
            return;
        }

        const uploadedUrls = {};

        for (const file of videos) {
            const filePath = path.join(videosDir, file);
            console.log(`\nFazendo upload de ${file}...`);
            
            const fileStream = fs.createReadStream(filePath);
            
            const { url } = await put(`videos/${file}`, fileStream, {
                access: 'public',
                token: token
            });
            
            console.log(`Upload concluído: ${url}`);
            uploadedUrls[file] = url;
        }
        
        console.log('\n--- UPLOAD FINALIZADO ---');
        console.log('Aqui estão as URLs dos vídeos:');
        console.log(JSON.stringify(uploadedUrls, null, 2));
        
        // Save mapping to a file
        fs.writeFileSync(path.join(__dirname, 'blob_urls.json'), JSON.stringify(uploadedUrls, null, 2));
        console.log('\nAs URLs foram salvas no arquivo blob_urls.json.');
        console.log('Agora você pode substituir as referências locais na página HTML por essas URLs.');

    } catch (error) {
        console.error('Ocorreu um erro ao fazer upload:', error);
    }
}

uploadVideos();
