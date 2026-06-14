const obj = {
  fname: "Fahadh",
  lname: "Muhammadh",
  age: 26,
  display: function () {
    console.log("Full Name: ", this.fname, " ", this.lname, "\n", "Age: ", this.age, "\n");
  },
};

obj.display();

const tree = fetch(".../tree.json")
  .then((res) => res.text())
  .then((data) => console.log(data));
