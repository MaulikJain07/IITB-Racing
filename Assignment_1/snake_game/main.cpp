#include<ncurses.h>
#include<deque>  //double header vector jo ki deque hai uske liye
#include<ctime>  //time ka kuch kuch karta
#include<cstdlib> //rand and srand iske function

enum Direction{UP,DOWN,RIGHT,LEFT};

struct Point{
    int x,y;
};

class Board{
    //ham width or height ko private rakhenge, aur niche ek constructor define kardenge jo isko value assign kardega
    private:    
        int width,height;

    public:
        Board(int w,int h){
            width = w;
            height = h;
        }

    void draw(){
        //clears the screen buffer
        clear();

        for(int i =0;i<width;i++){
            //horizontal walls, mvaddch(y,x) .
            mvaddch(0, i, '#');
            mvaddch(height-1, i, '#');   //in CPP, first line is (0,y) and uske niche y increases.  
        }
            //ab vertical walls
            for(int j=1;j<height;j++){
                mvaddch(j,0,'#');
                mvaddch(j,width-1,'#');
            }
        
    }

      // functions so that we can get dimensions for other classes
    int getwidth(){return width;}
    int getheight(){return height;}


};


class Snake{
    private:
        std::deque<Point> body;  //ek deque bnaya jismein points honge, name body
        Direction dir;

    public:
        Snake(int start_x,int start_y){
            //ek chota sa snake bnate hai...
            for(int i=0;i<3;i++){
                body.push_back({start_x-i,start_y});
            }
            dir = RIGHT ; //initial direction
        }

        void set_course(Direction new_dir){
            if ((dir == UP && new_dir != DOWN) || (dir == DOWN && new_dir != UP) ||
            (dir == LEFT && new_dir != RIGHT) || (dir == RIGHT && new_dir != LEFT)) {
            dir = new_dir;
        }

}

        void move(bool grow){
            Point head_point = body.front();
            if(dir==RIGHT) head_point.x++;
            if(dir==LEFT) head_point.x--;
            if(dir==DOWN) head_point.y++;
            if(dir==UP) head_point.y--;

            //snake aage badhta hai, uske aage wale point pe ek naya point generate hota hai, aur tail pe ek point eliminate.
            body.push_front(head_point);

        if(!grow) body.pop_back();
        }

        void draw(){
            for(auto const& segment : body){
                mvaddch(segment.y,segment.x,'O');
            }
        }
        std::deque<Point> getBody(){
            return body;
        }

};


class Food{
    private:
        Point pos;

    public:
        Food(){
            pos.x=0;   //initially kuch khali value deke define kardiya...
            pos.y=0;
        }
        void respawn(int w,int h){
            pos.x = (rand()%(w-2))+1;  
            pos.y = (rand()%(h-2))  +1;
        }

        void draw(){
            mvaddch(pos.y,pos.x,'*');  //* ayega food ki jagah
        }
        
        Point getPoint(){   //agar food ka location chahiye hoga, toh ye function kaam ayega...
            return pos;   
        }
        
};


class Game {
private:
    Snake snake;
    Food food;
    Board board;
    bool gameOver;
    int score;

public:
    // Initialize the game with a board size
    Game() : board(40, 20), snake(20, 10), gameOver(false), score(0) {
        srand(time(0)); // Seed randomness once
        food.respawn(board.getwidth(), board.getheight());
    }

    void handleInput() {
        int ch = getch(); // Get user key press
        switch (ch) {
            case 'w': case KEY_UP:    snake.set_course(UP); break;
            case 's': case KEY_DOWN:  snake.set_course(DOWN); break;
            case 'a': case KEY_LEFT:  snake.set_course(LEFT); break;
            case 'd': case KEY_RIGHT: snake.set_course(RIGHT); break;
            case 'q': gameOver = true; break;
        }
    }

    void update() {
        if (gameOver) return;

       
                  //  Get the current head position
            Point head = snake.getBody().front(); 

                       //  Check if the head is on the food
            if (head.x == food.getPoint().x && head.y == food.getPoint().y) {
                score ++;                     // Increase score
                food.respawn(board.getwidth(), board.getheight()); // Relocate food
                snake.move(true); 

    }
             else {
                        // Normal move: add a head and remove the tail
                snake.move(false); 
    }

                    // 3. Check for collisions (Wall or Self)
             if (checkCollision(head)) {
                 gameOver = true;
    }

}

    void render() {
        board.draw();
        food.draw();
        snake.draw();
        
        // Display score
        mvprintw(0, 0, "Score: %d", score); 
        refresh();
    }

    bool isOver() { return gameOver; }
};


int main(){
    srand(time(0));
    initscr(); //starts the screen
    noecho();  //doesnt show what the user types
    curs_set(0); //doesnt show the blinking cursor  

    Board gameboard(40,20);

    bool gameOver = false;

    while(!gameOver){
        gameboard.draw();
        refresh();

        if(getch()=='q') break; //quits the game.
    }
    
    endwin();
    return 0;
}