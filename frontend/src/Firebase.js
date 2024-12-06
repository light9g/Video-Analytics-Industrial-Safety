import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDu-DD6s7tO7hbtcvKcNzM_Y3yids_J6Rg",
  authDomain: "ibm-safety-net-f2a46.firebaseapp.com",
  projectId: "ibm-safety-net-f2a46",
  storageBucket: "ibm-safety-net-f2a46.appspot.com",
  messagingSenderId: "362598513958",
  appId: "1:362598513958:web:0d6d8199c4cf1924af95e7",
  measurementId: "G-HY0E3LL1TD"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export default app;
