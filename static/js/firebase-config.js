// firebase-config.js

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { 
    getAuth 
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCnaO2lREdHhfg95I632UdMT8MhRNVbovY",
  authDomain: "veza-abogados.firebaseapp.com",
  projectId: "veza-abogados",
  storageBucket: "veza-abogados.firebasestorage.app",
  messagingSenderId: "496741161381",
  appId: "1:496741161381:web:30b865bb6feca0e356304c"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);