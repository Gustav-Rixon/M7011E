
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>Register</h1>
      <div className ="form">
        <label> Name </label>
      <input type="text" name = "name"/>
      <label> Adress </label>
      <input type="text" name = "adress"/>
      <label> Zip </label>
      <input type="text" name = "zip"/>
      <label> Password </label>
      <input type="text" name = "password"/>
      <button>submit</button>
      </div>
    </div>
  );
}

export default App;
