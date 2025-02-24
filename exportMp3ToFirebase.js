const { initializeApp } = require("firebase/app");
const { getStorage, ref, uploadBytes, getDownloadURL } = require("firebase/storage");
const fs = require("fs");

// Captura o argumento passado na linha de comando
const localFilePath = process.argv[2];

if (!localFilePath) {
    console.error("Erro: Informe o caminho do arquivo como argumento.");
    process.exit(1);
}

// Defina o caminho no Firebase Storage (mude conforme necessário)
const fileName = localFilePath.split("/").pop(); // Obtém apenas o nome do arquivo
const storagePath = `musics/${fileName}`;

const firebaseConfig = {
    apiKey: "AIzaSyCBFRPGoyF6dr-DxvDiuYMbZIbgjOiWPEQ",
    authDomain: "lovestory-ca547.firebaseapp.com",
    projectId: "lovestory-ca547",
    storageBucket: "lovestory-ca547.firebasestorage.app",
    messagingSenderId: "247588040919",
    appId: "1:247588040919:web:9c31ad2b6f68767ffd4092",
    measurementId: "G-E0M2YWFY19"
};

const app = initializeApp(firebaseConfig);
const storage = getStorage(app);

// Lendo o arquivo
fs.readFile(localFilePath, (err, fileBuffer) => {
    if (err) {
        console.error("Erro ao ler o arquivo:", err);
        process.exit(1);
    }

    // Criando referência no Firebase Storage
    const storageRef = ref(storage, storagePath);

    // Fazendo o upload do arquivo
    uploadBytes(storageRef, fileBuffer).then((snapshot) => {
        // console.log("Upload concluído!", snapshot); // DEBUG

        // Obtendo a URL de download do arquivo
        getDownloadURL(storageRef).then((url) => {
            // console.log("Arquivo disponível em:", url);

            console.log(url);

            // Aqui você pode retornar o link ou processá-lo conforme necessário
            process.exit(0);  // Finaliza o script com sucesso
        }).catch((error) => {
            console.error("Erro ao obter o link de download:", error);
            process.exit(1);  // Finaliza o script com erro
        });
    }).catch((error) => {
        console.error("Erro ao enviar o arquivo:", error);
        process.exit(1);  // Finaliza o script com erro
    });
});
