import {
    S3Client,
    PutObjectCommand,
} from '@aws-sdk/client-s3';

const uploadkeys = {
    VITE_BUCKET:"mytest",
    VITE_PUBLIC_DOMAIN:"pub-c3213a95fe974e4285904cde8a7dafb6.r2.dev",
    VITE_CLOUDFLARE_ENDPOINT:"https://fd40d392fc6b30a82529534cf4c2ea74.r2.cloudflarestorage.com",
    VITE_CLOUDFLARE_ACCESSKEY_ID:"da405b1953116eef0de1744bb2578135",
    VITE_CLOUDFLARE_SECRET_ACCESSKEY:"6f6594481404399075036cc1a40e18683995f2d09b18d116832dfebf3aa02945"
}
function fileToUint8Array (file:File):Promise<Uint8Array> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const arrayBuffer = e.target!.result as ArrayBuffer;
            resolve(new Uint8Array(arrayBuffer));
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

export function uploadFile(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        console.log(uploadkeys.VITE_BUCKET);
        async function run() {
            const fileBuffer = await fileToUint8Array(file!);
            const fname = Date.now().toString();
            const input = { // ListBucketsRequest
                Bucket:uploadkeys.VITE_BUCKET,
                Key:fname,
                Body:fileBuffer,
                ContentType:"image/png",
            };
            const S3 = new S3Client({
                region: "auto",
                endpoint: uploadkeys.VITE_CLOUDFLARE_ENDPOINT,
                credentials: {
                    accessKeyId: uploadkeys.VITE_CLOUDFLARE_ACCESSKEY_ID,
                    secretAccessKey: uploadkeys.VITE_CLOUDFLARE_SECRET_ACCESSKEY,
                },
            });
            const command = new PutObjectCommand(input);
            await S3.send(command);
            const newSrc = "https://"+uploadkeys.VITE_PUBLIC_DOMAIN+"/" + fname;
            resolve(newSrc);
        }
        run();
    });

}